/**
 * Hyperswitch Payment Service for MedusaJS
 * $2000 Bounty Implementation
 * 
 * This service integrates Hyperswitch payment processing with MedusaJS
 */

import { PaymentService } from "@medusajs/medusa"
import axios from "axios"

class HyperswitchPaymentService extends PaymentService {
  static identifier = "hyperswitch"
  
  constructor({ regionService, customerService, totalsService, logger }, options) {
    super()
    
    this.regionService_ = regionService
    this.customerService_ = customerService
    this.totalsService_ = totalsService
    this.logger_ = logger
    
    // Hyperswitch configuration
    this.apiKey_ = options.api_key || process.env.HYPERSWITCH_API_KEY
    this.publishableKey_ = options.publishable_key || process.env.HYPERSWITCH_PUBLISHABLE_KEY
    this.apiUrl_ = options.api_url || "https://api.hyperswitch.io"
    this.webhookSecret_ = options.webhook_secret || process.env.HYPERSWITCH_WEBHOOK_SECRET
    
    // Proxy configuration for secure connections
    this.proxyConfig_ = options.proxy || null
  }

  /**
   * Get payment data
   */
  async getPaymentData(sessionData) {
    try {
      return sessionData
    } catch (error) {
      this.logger_.error(`Hyperswitch: Error getting payment data: ${error.message}`)
      throw error
    }
  }

  /**
   * Update payment data
   */
  async updatePaymentData(sessionData, update) {
    try {
      return { ...sessionData, ...update }
    } catch (error) {
      this.logger_.error(`Hyperswitch: Error updating payment data: ${error.message}`)
      throw error
    }
  }

  /**
   * Create payment session
   */
  async createPayment(cart) {
    try {
      const { region_id, total, customer_id, context } = cart
      const region = await this.regionService_.retrieve(region_id)
      
      // Create payment intent with Hyperswitch
      const paymentData = {
        amount: Math.round(total),
        currency: region.currency_code.toUpperCase(),
        customer_id: customer_id,
        capture_method: "manual",
        metadata: {
          cart_id: cart.id,
          medusa_payment: true
        }
      }

      const response = await this.makeApiRequest("POST", "/payments/create", paymentData)
      
      return {
        session_data: {
          payment_intent_id: response.payment_id,
          client_secret: response.client_secret,
          publishable_key: this.publishableKey_
        }
      }
    } catch (error) {
      this.logger_.error(`Hyperswitch: Error creating payment: ${error.message}`)
      throw error
    }
  }

  /**
   * Update payment session
   */
  async updatePayment(sessionData, cart) {
    try {
      const { payment_intent_id } = sessionData
      const { total } = cart
      
      const updateData = {
        payment_id: payment_intent_id,
        amount: Math.round(total)
      }
      
      await this.makeApiRequest("POST", `/payments/${payment_intent_id}/update`, updateData)
      
      return sessionData
    } catch (error) {
      this.logger_.error(`Hyperswitch: Error updating payment: ${error.message}`)
      throw error
    }
  }

  /**
   * Delete payment session
   */
  async deletePayment(payment) {
    try {
      const { payment_intent_id } = payment.data
      
      if (payment_intent_id) {
        await this.makeApiRequest("POST", `/payments/${payment_intent_id}/cancel`)
      }
      
      return payment
    } catch (error) {
      this.logger_.error(`Hyperswitch: Error deleting payment: ${error.message}`)
      throw error
    }
  }

  /**
   * Retrieve payment
   */
  async retrievePayment(paymentData) {
    try {
      const { payment_intent_id } = paymentData
      
      const response = await this.makeApiRequest("GET", `/payments/${payment_intent_id}`)
      
      return response
    } catch (error) {
      this.logger_.error(`Hyperswitch: Error retrieving payment: ${error.message}`)
      throw error
    }
  }

  /**
   * Get payment status
   */
  async getStatus(paymentData) {
    try {
      const { payment_intent_id } = paymentData
      
      const payment = await this.retrievePayment({ payment_intent_id })
      
      switch (payment.status) {
        case "succeeded":
        case "processing":
          return "authorized"
        case "requires_capture":
          return "pending"
        case "cancelled":
          return "canceled"
        case "failed":
          return "error"
        default:
          return "pending"
      }
    } catch (error) {
      this.logger_.error(`Hyperswitch: Error getting status: ${error.message}`)
      return "error"
    }
  }

  /**
   * Capture payment
   */
  async capturePayment(payment) {
    try {
      const { payment_intent_id } = payment.data
      
      const captureData = {
        payment_id: payment_intent_id,
        amount: payment.amount
      }
      
      const response = await this.makeApiRequest("POST", `/payments/${payment_intent_id}/capture`, captureData)
      
      return response
    } catch (error) {
      this.logger_.error(`Hyperswitch: Error capturing payment: ${error.message}`)
      throw error
    }
  }

  /**
   * Refund payment
   */
  async refundPayment(payment, refundAmount) {
    try {
      const { payment_intent_id } = payment.data
      
      const refundData = {
        payment_id: payment_intent_id,
        amount: Math.round(refundAmount),
        reason: "requested_by_customer"
      }
      
      const response = await this.makeApiRequest("POST", "/refunds/create", refundData)
      
      return response
    } catch (error) {
      this.logger_.error(`Hyperswitch: Error refunding payment: ${error.message}`)
      throw error
    }
  }

  /**
   * Cancel payment
   */
  async cancelPayment(payment) {
    try {
      const { payment_intent_id } = payment.data
      
      const response = await this.makeApiRequest("POST", `/payments/${payment_intent_id}/cancel`)
      
      return response
    } catch (error) {
      this.logger_.error(`Hyperswitch: Error canceling payment: ${error.message}`)
      throw error
    }
  }

  /**
   * Make API request to Hyperswitch
   */
  async makeApiRequest(method, endpoint, data = null) {
    try {
      const config = {
        method,
        url: `${this.apiUrl_}${endpoint}`,
        headers: {
          "api-key": this.apiKey_,
          "Content-Type": "application/json"
        }
      }
      
      if (data) {
        config.data = data
      }
      
      // Add proxy support if configured
      if (this.proxyConfig_) {
        config.proxy = this.proxyConfig_
      }
      
      const response = await axios(config)
      return response.data
      
    } catch (error) {
      this.logger_.error(`Hyperswitch API Error: ${error.message}`)
      if (error.response) {
        this.logger_.error(`Response data: ${JSON.stringify(error.response.data)}`)
      }
      throw error
    }
  }

  /**
   * Verify webhook signature
   */
  verifyWebhook(payload, signature) {
    try {
      const crypto = require('crypto')
      const expectedSignature = crypto
        .createHmac('sha256', this.webhookSecret_)
        .update(payload)
        .digest('hex')
      
      return signature === expectedSignature
    } catch (error) {
      this.logger_.error(`Hyperswitch: Error verifying webhook: ${error.message}`)
      return false
    }
  }
}

export default HyperswitchPaymentService