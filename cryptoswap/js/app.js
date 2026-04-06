// ============================================
// SwapVault - Main Application JavaScript
// ============================================

// ---- NAVBAR ----
const navbar = document.getElementById('navbar');
const mobileToggle = document.getElementById('mobileToggle');
const navLinks = document.getElementById('navLinks');

window.addEventListener('scroll', () => {
    if (window.scrollY > 50) {
        navbar.classList.add('scrolled');
    } else {
        navbar.classList.remove('scrolled');
    }
});

mobileToggle.addEventListener('click', () => {
    navLinks.classList.toggle('active');
});

// Close mobile menu on link click
document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', () => {
        navLinks.classList.remove('active');
    });
});

// ---- LIVE PRICE DATA ----
const COINGECKO_API = 'https://api.coingecko.com/api/v3';

const TOP_COINS = [
    'bitcoin', 'ethereum', 'binancecoin', 'solana', 'ripple',
    'cardano', 'dogecoin', 'tron', 'polkadot', 'avalanche-2',
    'chainlink', 'polygon-ecosystem-token', 'litecoin', 'uniswap', 'stellar'
];

const COIN_SYMBOLS = {
    'bitcoin': 'BTC', 'ethereum': 'ETH', 'binancecoin': 'BNB',
    'solana': 'SOL', 'ripple': 'XRP', 'cardano': 'ADA',
    'dogecoin': 'DOGE', 'tron': 'TRX', 'polkadot': 'DOT',
    'avalanche-2': 'AVAX', 'chainlink': 'LINK',
    'polygon-ecosystem-token': 'POL', 'litecoin': 'LTC',
    'uniswap': 'UNI', 'stellar': 'XLM'
};

const COIN_NAMES = {
    'bitcoin': 'Bitcoin', 'ethereum': 'Ethereum', 'binancecoin': 'BNB',
    'solana': 'Solana', 'ripple': 'XRP', 'cardano': 'Cardano',
    'dogecoin': 'Dogecoin', 'tron': 'TRON', 'polkadot': 'Polkadot',
    'avalanche-2': 'Avalanche', 'chainlink': 'Chainlink',
    'polygon-ecosystem-token': 'Polygon', 'litecoin': 'Litecoin',
    'uniswap': 'Uniswap', 'stellar': 'Stellar'
};

let priceData = {};

async function fetchPrices() {
    try {
        const ids = TOP_COINS.join(',');
        const response = await fetch(
            `${COINGECKO_API}/simple/price?ids=${ids}&vs_currencies=usd&include_24hr_change=true&include_market_cap=true`
        );
        
        if (!response.ok) throw new Error('API error');
        
        priceData = await response.json();
        updatePriceTable();
        updateTicker();
        updateCalculator();
        updatePopularPairs();
    } catch (error) {
        console.log('Using fallback data');
        useFallbackData();
    }
}

function useFallbackData() {
    // Fallback prices in case API is rate-limited
    const fallback = {
        bitcoin: { usd: 84521, usd_24h_change: 2.34, usd_market_cap: 1678000000000 },
        ethereum: { usd: 3456, usd_24h_change: -1.12, usd_market_cap: 415000000000 },
        binancecoin: { usd: 612, usd_24h_change: 0.87, usd_market_cap: 91000000000 },
        solana: { usd: 178, usd_24h_change: 4.56, usd_market_cap: 82000000000 },
        ripple: { usd: 2.18, usd_24h_change: -0.45, usd_market_cap: 120000000000 },
        cardano: { usd: 0.72, usd_24h_change: 1.23, usd_market_cap: 25400000000 },
        dogecoin: { usd: 0.185, usd_24h_change: 3.21, usd_market_cap: 27000000000 },
        tron: { usd: 0.245, usd_24h_change: -0.78, usd_market_cap: 21000000000 },
        polkadot: { usd: 7.82, usd_24h_change: 2.1, usd_market_cap: 10600000000 },
        'avalanche-2': { usd: 38.5, usd_24h_change: -1.5, usd_market_cap: 15500000000 },
        chainlink: { usd: 16.4, usd_24h_change: 1.8, usd_market_cap: 10200000000 },
        'polygon-ecosystem-token': { usd: 0.52, usd_24h_change: -2.1, usd_market_cap: 5100000000 },
        litecoin: { usd: 92.3, usd_24h_change: 0.45, usd_market_cap: 6900000000 },
        uniswap: { usd: 12.8, usd_24h_change: 3.4, usd_market_cap: 9700000000 },
        stellar: { usd: 0.128, usd_24h_change: -0.9, usd_market_cap: 3800000000 }
    };
    
    priceData = fallback;
    updatePriceTable();
    updateTicker();
    updateCalculator();
    updatePopularPairs();
}

function formatPrice(price) {
    if (price >= 1000) return '$' + price.toLocaleString('en-US', { maximumFractionDigits: 0 });
    if (price >= 1) return '$' + price.toLocaleString('en-US', { maximumFractionDigits: 2 });
    return '$' + price.toLocaleString('en-US', { maximumFractionDigits: 4 });
}

function formatMarketCap(cap) {
    if (cap >= 1e12) return '$' + (cap / 1e12).toFixed(2) + 'T';
    if (cap >= 1e9) return '$' + (cap / 1e9).toFixed(2) + 'B';
    if (cap >= 1e6) return '$' + (cap / 1e6).toFixed(2) + 'M';
    return '$' + cap.toLocaleString();
}

function updatePriceTable() {
    const tbody = document.getElementById('pricesBody');
    if (!tbody) return;
    
    let html = '';
    let index = 1;
    
    for (const id of TOP_COINS) {
        const coin = priceData[id];
        if (!coin) continue;
        
        const change = coin.usd_24h_change || 0;
        const changeClass = change >= 0 ? 'price-positive' : 'price-negative';
        const changePrefix = change >= 0 ? '+' : '';
        const symbol = COIN_SYMBOLS[id] || id.toUpperCase();
        const name = COIN_NAMES[id] || id;
        
        html += `
            <tr>
                <td>${index}</td>
                <td>
                    <div class="coin-info">
                        <div class="coin-icon">${symbol.substring(0, 3)}</div>
                        <div>
                            <div class="coin-name">${name}</div>
                            <div class="coin-symbol">${symbol}</div>
                        </div>
                    </div>
                </td>
                <td><strong>${formatPrice(coin.usd)}</strong></td>
                <td class="${changeClass}">${changePrefix}${change.toFixed(2)}%</td>
                <td>${formatMarketCap(coin.usd_market_cap || 0)}</td>
                <td><a href="#exchange" class="btn btn-primary btn-sm">Exchange</a></td>
            </tr>
        `;
        index++;
    }
    
    tbody.innerHTML = html;
}

function updateTicker() {
    const ticker = document.getElementById('priceTicker');
    if (!ticker) return;
    
    let html = '';
    
    // Double the items for seamless scrolling
    for (let i = 0; i < 2; i++) {
        for (const id of TOP_COINS) {
            const coin = priceData[id];
            if (!coin) continue;
            
            const change = coin.usd_24h_change || 0;
            const changeClass = change >= 0 ? 'positive' : 'negative';
            const changePrefix = change >= 0 ? '+' : '';
            const symbol = COIN_SYMBOLS[id] || id.toUpperCase();
            
            html += `
                <div class="ticker-item">
                    <span class="name">${symbol}</span>
                    <span class="price">${formatPrice(coin.usd)}</span>
                    <span class="change ${changeClass}">${changePrefix}${change.toFixed(2)}%</span>
                </div>
            `;
        }
    }
    
    ticker.innerHTML = html;
}

function updatePopularPairs() {
    const grid = document.getElementById('popularGrid');
    if (!grid) return;
    
    const pairs = [
        { from: 'bitcoin', to: 'ethereum' },
        { from: 'ethereum', to: 'binancecoin' },
        { from: 'bitcoin', to: 'solana' },
        { from: 'ethereum', to: 'ripple' },
        { from: 'bitcoin', to: 'cardano' },
        { from: 'solana', to: 'ethereum' },
        { from: 'bitcoin', to: 'dogecoin' },
        { from: 'ethereum', to: 'tron' }
    ];
    
    let html = '';
    
    for (const pair of pairs) {
        const fromPrice = priceData[pair.from]?.usd || 0;
        const toPrice = priceData[pair.to]?.usd || 0;
        const rate = toPrice > 0 ? (fromPrice / toPrice).toFixed(4) : '...';
        const fromSymbol = COIN_SYMBOLS[pair.from];
        const toSymbol = COIN_SYMBOLS[pair.to];
        
        html += `
            <a href="#exchange" class="popular-card">
                <div class="popular-pair">${fromSymbol} &#x2192; ${toSymbol}</div>
                <div class="popular-rate">1 ${fromSymbol} = ${rate} ${toSymbol}</div>
            </a>
        `;
    }
    
    grid.innerHTML = html;
}

// ---- CALCULATOR ----
function updateCalculator() {
    const amount = parseFloat(document.getElementById('calcAmount')?.value) || 0;
    const fromId = document.getElementById('calcFrom')?.value;
    const toId = document.getElementById('calcTo')?.value;
    
    if (!fromId || !toId || !priceData[fromId] || !priceData[toId]) return;
    
    const fromPrice = priceData[fromId].usd;
    const toPrice = priceData[toId].usd;
    const result = (amount * fromPrice) / toPrice;
    
    const resultEl = document.getElementById('calcResult');
    if (resultEl) resultEl.value = result.toFixed(8);
    
    const rateEl = document.getElementById('calcRate');
    const fromSymbol = COIN_SYMBOLS[fromId] || fromId.toUpperCase();
    const toSymbol = COIN_SYMBOLS[toId] || toId.toUpperCase();
    if (rateEl) {
        rateEl.textContent = `1 ${fromSymbol} = ${(fromPrice / toPrice).toFixed(8)} ${toSymbol}`;
    }
}

// Calculator event listeners
document.getElementById('calcAmount')?.addEventListener('input', updateCalculator);
document.getElementById('calcFrom')?.addEventListener('change', updateCalculator);
document.getElementById('calcTo')?.addEventListener('change', updateCalculator);

document.getElementById('calcSwap')?.addEventListener('click', () => {
    const fromEl = document.getElementById('calcFrom');
    const toEl = document.getElementById('calcTo');
    const temp = fromEl.value;
    fromEl.value = toEl.value;
    toEl.value = temp;
    updateCalculator();
});

// ---- FAQ ----
document.querySelectorAll('.faq-question').forEach(btn => {
    btn.addEventListener('click', () => {
        const item = btn.parentElement;
        const isActive = item.classList.contains('active');
        
        // Close all
        document.querySelectorAll('.faq-item').forEach(faq => {
            faq.classList.remove('active');
        });
        
        // Open clicked if wasn't active
        if (!isActive) {
            item.classList.add('active');
        }
    });
});

// ---- SMOOTH SCROLL ----
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            const offset = 80;
            const position = target.getBoundingClientRect().top + window.scrollY - offset;
            window.scrollTo({ top: position, behavior: 'smooth' });
        }
    });
});

// ---- ACTIVE NAV LINK ----
const sections = document.querySelectorAll('section[id]');
window.addEventListener('scroll', () => {
    const scrollY = window.scrollY + 100;
    
    sections.forEach(section => {
        const top = section.offsetTop;
        const height = section.offsetHeight;
        const id = section.getAttribute('id');
        
        if (scrollY >= top && scrollY < top + height) {
            document.querySelectorAll('.nav-link').forEach(link => {
                link.classList.remove('active');
                if (link.getAttribute('href') === `#${id}`) {
                    link.classList.add('active');
                }
            });
        }
    });
});

// ---- INTERSECTION OBSERVER FOR ANIMATIONS ----
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('animate-in');
        }
    });
}, observerOptions);

document.querySelectorAll('.feature-card, .step-card, .popular-card').forEach(el => {
    observer.observe(el);
});

// ---- INITIALIZE ----
fetchPrices();

// Refresh prices every 60 seconds
setInterval(fetchPrices, 60000);

// ---- SEO: Structured Data ----
const structuredData = {
    "@context": "https://schema.org",
    "@type": "WebApplication",
    "name": "SwapVault",
    "description": "Exchange 1500+ cryptocurrencies instantly with the best rates. No registration required.",
    "url": window.location.href,
    "applicationCategory": "FinanceApplication",
    "operatingSystem": "Web",
    "offers": {
        "@type": "Offer",
        "price": "0",
        "priceCurrency": "USD"
    }
};

const scriptEl = document.createElement('script');
scriptEl.type = 'application/ld+json';
scriptEl.textContent = JSON.stringify(structuredData);
document.head.appendChild(scriptEl);
