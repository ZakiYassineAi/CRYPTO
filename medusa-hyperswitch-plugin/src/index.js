/**
 * Hyperswitch Payment Plugin for MedusaJS
 * Entry point for the plugin
 */

export default {
  /**
   * Plugin configuration
   */
  getConfigTemplate() {
    return {
      api_key: {
        type: "string",
        required: true,
        description: "Hyperswitch API Key"
      },
      publishable_key: {
        type: "string", 
        required: true,
        description: "Hyperswitch Publishable Key"
      },
      api_url: {
        type: "string",
        default: "https://api.hyperswitch.io",
        description: "Hyperswitch API URL"
      },
      webhook_secret: {
        type: "string",
        required: false,
        description: "Webhook signing secret"
      },
      proxy: {
        type: "object",
        required: false,
        description: "Proxy configuration for API requests"
      }
    }
  }
}