/**
 * Test suite for Hyperswitch Payment Service
 */

import HyperswitchPaymentService from "../src/services/hyperswitch-payment"

describe("HyperswitchPaymentService", () => {
  let service
  let mockLogger
  
  beforeEach(() => {
    mockLogger = {
      error: jest.fn(),
      info: jest.fn(),
      warn: jest.fn()
    }
    
    const options = {
      api_key: "test_api_key",
      publishable_key: "test_pub_key",
      api_url: "https://api.test.hyperswitch.io"
    }
    
    service = new HyperswitchPaymentService(
      {
        regionService: {},
        customerService: {},
        totalsService: {},
        logger: mockLogger
      },
      options
    )
  })
  
  describe("createPayment", () => {
    it("should create a payment session", async () => {
      const cart = {
        id: "cart_123",
        region_id: "reg_123",
        total: 10000,
        customer_id: "cust_123"
      }
      
      // Mock region service
      service.regionService_.retrieve = jest.fn().mockResolvedValue({
        currency_code: "usd"
      })
      
      // Mock API request
      service.makeApiRequest = jest.fn().mockResolvedValue({
        payment_id: "pay_123",
        client_secret: "secret_123"
      })
      
      const result = await service.createPayment(cart)
      
      expect(result.session_data).toHaveProperty("payment_intent_id")
      expect(result.session_data).toHaveProperty("client_secret")
      expect(result.session_data).toHaveProperty("publishable_key")
    })
  })
  
  describe("capturePayment", () => {
    it("should capture an authorized payment", async () => {
      const payment = {
        data: {
          payment_intent_id: "pay_123"
        },
        amount: 10000
      }
      
      service.makeApiRequest = jest.fn().mockResolvedValue({
        status: "captured"
      })
      
      const result = await service.capturePayment(payment)
      
      expect(result.status).toBe("captured")
      expect(service.makeApiRequest).toHaveBeenCalledWith(
        "POST",
        "/payments/pay_123/capture",
        expect.objectContaining({
          payment_id: "pay_123",
          amount: 10000
        })
      )
    })
  })
  
  describe("refundPayment", () => {
    it("should create a refund", async () => {
      const payment = {
        data: {
          payment_intent_id: "pay_123"
        }
      }
      const refundAmount = 5000
      
      service.makeApiRequest = jest.fn().mockResolvedValue({
        refund_id: "ref_123",
        status: "succeeded"
      })
      
      const result = await service.refundPayment(payment, refundAmount)
      
      expect(result.refund_id).toBe("ref_123")
      expect(service.makeApiRequest).toHaveBeenCalledWith(
        "POST",
        "/refunds/create",
        expect.objectContaining({
          payment_id: "pay_123",
          amount: 5000
        })
      )
    })
  })
  
  describe("verifyWebhook", () => {
    it("should verify webhook signature", () => {
      service.webhookSecret_ = "webhook_secret"
      
      const payload = '{"event":"payment.succeeded"}'
      const crypto = require('crypto')
      const validSignature = crypto
        .createHmac('sha256', 'webhook_secret')
        .update(payload)
        .digest('hex')
      
      const result = service.verifyWebhook(payload, validSignature)
      
      expect(result).toBe(true)
    })
    
    it("should reject invalid signature", () => {
      service.webhookSecret_ = "webhook_secret"
      
      const payload = '{"event":"payment.succeeded"}'
      const invalidSignature = "invalid_signature"
      
      const result = service.verifyWebhook(payload, invalidSignature)
      
      expect(result).toBe(false)
    })
  })
  
  describe("getStatus", () => {
    it("should map Hyperswitch status to Medusa status", async () => {
      const testCases = [
        { hyperswitchStatus: "succeeded", expectedStatus: "authorized" },
        { hyperswitchStatus: "processing", expectedStatus: "authorized" },
        { hyperswitchStatus: "requires_capture", expectedStatus: "pending" },
        { hyperswitchStatus: "cancelled", expectedStatus: "canceled" },
        { hyperswitchStatus: "failed", expectedStatus: "error" }
      ]
      
      for (const testCase of testCases) {
        service.retrievePayment = jest.fn().mockResolvedValue({
          status: testCase.hyperswitchStatus
        })
        
        const status = await service.getStatus({ payment_intent_id: "pay_123" })
        
        expect(status).toBe(testCase.expectedStatus)
      }
    })
  })
})

// Export for Jest
export default HyperswitchPaymentService