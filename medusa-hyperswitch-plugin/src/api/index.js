/**
 * API Routes for Hyperswitch Webhooks
 */

import { Router } from "express"
import bodyParser from "body-parser"

export default (rootDirectory, options) => {
  const router = Router()
  
  // Webhook endpoint
  router.post(
    "/hyperswitch/webhooks",
    bodyParser.raw({ type: "application/json" }),
    async (req, res) => {
      const hyperswitchService = req.scope.resolve("hyperswitchPaymentService")
      const orderService = req.scope.resolve("orderService")
      
      try {
        // Verify webhook signature
        const signature = req.headers["x-hyperswitch-signature"]
        const isValid = hyperswitchService.verifyWebhook(req.body.toString(), signature)
        
        if (!isValid) {
          return res.status(400).json({ error: "Invalid signature" })
        }
        
        const event = JSON.parse(req.body.toString())
        
        // Handle different event types
        switch (event.type) {
          case "payment.succeeded":
            await handlePaymentSucceeded(event, orderService)
            break
          case "payment.failed":
            await handlePaymentFailed(event, orderService)
            break
          case "refund.succeeded":
            await handleRefundSucceeded(event, orderService)
            break
          default:
            console.log(`Unhandled event type: ${event.type}`)
        }
        
        res.sendStatus(200)
      } catch (error) {
        console.error("Webhook error:", error)
        res.status(400).json({ error: error.message })
      }
    }
  )
  
  return router
}

async function handlePaymentSucceeded(event, orderService) {
  const { payment_id, metadata } = event.data
  
  if (metadata?.cart_id) {
    // Update order status
    await orderService.capturePayment(metadata.cart_id)
  }
}

async function handlePaymentFailed(event, orderService) {
  const { metadata } = event.data
  
  if (metadata?.cart_id) {
    // Handle failed payment
    console.log(`Payment failed for cart ${metadata.cart_id}`)
  }
}

async function handleRefundSucceeded(event, orderService) {
  const { refund_id, payment_id } = event.data
  console.log(`Refund ${refund_id} succeeded for payment ${payment_id}`)
}