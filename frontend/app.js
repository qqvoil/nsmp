// NeverSMP Donation Store Frontend Logic

let catalogItems = [];
let tokenPackages = [];
let selectedTier = 30;
let currentCurrency = 'rub'; // 'rub' or 'tokens'
let selectedCheckoutItem = null;
let currentDiscount = 0;
let appliedPromo = "";

// Base exchange rate: 1 RUB = 25 Tokens
const BASE_TOKENS_PER_RUB = 25;

const PREMIUM_TIERS_DATA = {
    30: { name: "Премиум на 30 дней", rub: 99, tokens: 15000, badge: "Подписка 30 дней", itemId: "premium_30" },
    60: { name: "Премиум на 60 дней", rub: 149, tokens: 25000, badge: "Выгодно -25%", itemId: "premium_60" },
    90: { name: "Премиум на 90 дней", rub: 249, tokens: 40000, badge: "Хит -35%", itemId: "premium_90" }
};

document.addEventListener('DOMContentLoaded', () => {
    initCopyIp();
    initPremiumTiers();
    initTokenSlider();
    initTokenPackages();
    initCheckoutModal();
    initTokenInstructionModal();
    loadCatalog();
    loadRecentDonates();
    checkUrlParams();
});

// 1. Copy IP to Clipboard
function initCopyIp() {
    const copyBtn = document.getElementById('copy-ip-btn');
    const copyHint = document.getElementById('copy-hint');
    if (!copyBtn) return;

    copyBtn.addEventListener('click', () => {
        navigator.clipboard.writeText('mc.neversmp.ru').then(() => {
            copyHint.textContent = 'Скопировано!';
            copyHint.style.color = '#2ed573';
            setTimeout(() => {
                copyHint.textContent = 'Скопировать';
                copyHint.style.color = '';
            }, 2000);
        });
    });
}

// 2. Premium Tiers & Currency Switcher
function initPremiumTiers() {
    const tierCards = document.querySelectorAll('.tier-card');
    const rubBtn = document.getElementById('curr-rub-btn');
    const tokBtn = document.getElementById('curr-tok-btn');
    const buyBtn = document.getElementById('buy-premium-btn');

    tierCards.forEach(card => {
        card.addEventListener('click', () => {
            tierCards.forEach(c => c.classList.remove('active'));
            card.classList.add('active');
            selectedTier = parseInt(card.getAttribute('data-tier'), 10);
            updatePremiumCta();
        });
    });

    if (rubBtn && tokBtn) {
        rubBtn.addEventListener('click', () => {
            currentCurrency = 'rub';
            rubBtn.classList.add('active');
            tokBtn.classList.remove('active');
            updateTierPricesDisplay();
            updatePremiumCta();
        });

        tokBtn.addEventListener('click', () => {
            currentCurrency = 'tokens';
            tokBtn.classList.add('active');
            rubBtn.classList.remove('active');
            updateTierPricesDisplay();
            updatePremiumCta();
        });
    }

    if (buyBtn) {
        buyBtn.addEventListener('click', () => {
            const tierData = PREMIUM_TIERS_DATA[selectedTier];
            if (currentCurrency === 'rub') {
                openCheckoutModal(tierData.itemId);
            } else {
                openTokenInstructionModal();
            }
        });
    }

    updateTierPricesDisplay();
    updatePremiumCta();
}

function updateTierPricesDisplay() {
    const priceElems = document.querySelectorAll('.tier-cost .price-val');
    priceElems.forEach(elem => {
        if (currentCurrency === 'rub') {
            elem.textContent = elem.getAttribute('data-rub');
        } else {
            elem.textContent = elem.getAttribute('data-tok');
        }
    });
}

function updatePremiumCta() {
    const tierData = PREMIUM_TIERS_DATA[selectedTier];
    const priceDisplay = document.getElementById('selected-tier-price');
    const buyBtnText = document.querySelector('#buy-premium-btn span');
    
    if (currentCurrency === 'rub') {
        let finalPrice = tierData.rub;
        if (currentDiscount > 0) {
            finalPrice = Math.max(1, Math.round(tierData.rub * (1 - currentDiscount / 100.0)));
        }
        if (priceDisplay) priceDisplay.textContent = `${finalPrice} ₽`;
        if (buyBtnText) buyBtnText.innerHTML = `Оформить Премиум за <strong id="selected-tier-price">${finalPrice} ₽</strong>`;
    } else {
        const formattedTokens = `${tierData.tokens.toLocaleString('ru-RU')} т`;
        if (buyBtnText) buyBtnText.innerHTML = `Купить в игре за <strong>${formattedTokens}</strong>`;
    }
}

// 3. Interactive Token Slider Calculator
function initTokenSlider() {
    const slider = document.getElementById('tokens-range-slider');
    const tokensVal = document.getElementById('calc-tokens-val');
    const priceVal = document.getElementById('calc-price-val');
    const basePriceVal = document.getElementById('calc-base-price');
    const badge = document.getElementById('calc-discount-badge');
    const btnTokensAmount = document.getElementById('btn-tokens-amount');
    const btnTokensPrice = document.getElementById('btn-tokens-price');
    const buyBtn = document.getElementById('buy-calc-tokens-btn');

    if (!slider) return;

    function updateSlider() {
        const tokens = parseInt(slider.value, 10);
        const min = parseInt(slider.min, 10);
        const max = parseInt(slider.max, 10);
        const basePrice = tokens / BASE_TOKENS_PER_RUB;

        // Progressive discount up to 30% at 100k
        const progress = Math.max(0, Math.min(1, (tokens - min) / (max - min)));
        let discountPct = Math.round(progress * 30.0);
        
        // Add global promo code discount if applied
        if (currentDiscount > 0) {
            discountPct = Math.min(99, discountPct + currentDiscount);
        }

        const finalPrice = Math.max(10, Math.round(basePrice * (1 - discountPct / 100.0)));

        const formattedTokens = tokens.toLocaleString('ru-RU');
        tokensVal.textContent = formattedTokens;
        priceVal.textContent = `${finalPrice} ₽`;
        
        if (discountPct > 0) {
            basePriceVal.textContent = `${Math.round(basePrice)} ₽`;
            basePriceVal.style.display = 'inline';
            badge.textContent = `Скидка: ${discountPct}%`;
            badge.style.display = 'inline-block';
        } else {
            basePriceVal.style.display = 'none';
            badge.textContent = 'Базовый курс';
        }

        btnTokensAmount.textContent = formattedTokens;
        btnTokensPrice.textContent = `${finalPrice} ₽`;

        // Update slider fill track
        const fillPercent = progress * 100;
        slider.style.background = `linear-gradient(to right, #f59e0b 0%, #f59e0b ${fillPercent}%, rgba(255,255,255,0.1) ${fillPercent}%, rgba(255,255,255,0.1) 100%)`;
    }

    slider.addEventListener('input', updateSlider);
    updateSlider();

    if (buyBtn) {
        buyBtn.addEventListener('click', () => {
            const tokens = parseInt(slider.value, 10);
            openCheckoutForCustomTokens(tokens);
        });
    }
}

// 4. Token Packages Grid
function initTokenPackages() {
    const grid = document.getElementById('token-packages-grid');
    if (!grid) return;

    const packages = [
        { id: "tokens_1k", tokens: 1000, price: 40, discount: 0, badge: "Старт" },
        { id: "tokens_5k", tokens: 5000, price: 189, discount: 5, badge: "5% Скидка" },
        { id: "tokens_15k", tokens: 15000, price: 539, discount: 10, badge: "Хит • Хватит на Премиум!" },
        { id: "tokens_30k", tokens: 30000, price: 999, discount: 17, badge: "17% Скидка" },
        { id: "tokens_50k", tokens: 50000, price: 1549, discount: 23, badge: "23% Скидка" },
        { id: "tokens_100k", tokens: 100000, price: 2799, discount: 30, badge: "🔥 МАКС. 30%" }
    ];

    grid.innerHTML = packages.map(pkg => `
        <div class="package-card">
            ${pkg.badge ? `<div class="pkg-badge ${pkg.discount >= 20 ? 'gold' : ''}">${pkg.badge}</div>` : ''}
            <div>
                <h4 class="pkg-tokens">${pkg.tokens.toLocaleString('ru-RU')} Токенов</h4>
                <p class="pkg-desc">${pkg.discount > 0 ? `Экономия со скидкой ${pkg.discount}%` : 'Базовый стартовый пакет'}</p>
            </div>
            <div class="pkg-bottom">
                <span class="pkg-price">${pkg.price} ₽</span>
                <button class="pkg-btn" onclick="openCheckoutModal('${pkg.id}')">Купить</button>
            </div>
        </div>
    `).join('');
}

// 5. Checkout Modal & Skin Preview
function initCheckoutModal() {
    const modal = document.getElementById('checkout-modal');
    const closeBtn = document.getElementById('modal-close-btn');
    const nickInput = document.getElementById('player-nick');
    const avatarPreview = document.getElementById('avatar-preview');
    const form = document.getElementById('purchase-form');
    const promoInput = document.getElementById('promo-code');
    const applyPromoBtn = document.getElementById('apply-promo-btn');
    const promoMsg = document.getElementById('promo-msg');
    let selectedPlatform = 'java';

    // Platform Tab Switcher
    const platformTabs = document.querySelectorAll('.platform-tab');
    const nickLabel = document.getElementById('nick-field-label');
    const nickHint = document.getElementById('nick-field-hint');

    platformTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            platformTabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            selectedPlatform = tab.dataset.platform;

            if (selectedPlatform === 'bedrock') {
                nickLabel.textContent = 'Ваш никнейм в Bedrock (Телефон / Консоль)';
                nickInput.placeholder = 'Например: Steve (точка добавится автоматически)';
                nickHint.textContent = 'Для игроков с телефонов перед ником будет автоматически добавлен префикс точки (.)';
            } else {
                nickLabel.textContent = 'Ваш никнейм в Java Edition (ПК)';
                nickInput.placeholder = 'Например: qqvoil';
                nickHint.textContent = 'Убедитесь в правильности написания ника (с учетом регистра).';
            }
        });
    });

    if (closeBtn) {
        closeBtn.addEventListener('click', () => modal.classList.remove('active'));
    }

    let nickTimeout;
    if (nickInput) {
        nickInput.addEventListener('input', () => {
            clearTimeout(nickTimeout);
            let nick = nickInput.value.trim();
            if (nick.startsWith('.')) nick = nick.substring(1);
            nickTimeout = setTimeout(() => {
                if (nick.length >= 3) {
                    avatarPreview.src = `https://minotar.net/helm/${encodeURIComponent(nick)}/40.png`;
                } else {
                    avatarPreview.src = 'https://minotar.net/helm/Steve/40.png';
                }
            }, 300);
        });
    }

    if (applyPromoBtn) {
        applyPromoBtn.addEventListener('click', async () => {
            const code = (promoInput.value || '').trim().toUpperCase();
            if (!code) return;

            try {
                const resp = await fetch(`/api/check_promo?code=${encodeURIComponent(code)}`);
                const data = await resp.json();

                if (data.success) {
                    currentDiscount = data.discount_percent;
                    appliedPromo = code;
                    promoMsg.className = 'promo-msg success';
                    promoMsg.textContent = `✓ Промокод применен: скидка ${currentDiscount}%!`;
                    updateModalPrices();
                } else {
                    currentDiscount = 0;
                    appliedPromo = null;
                    promoMsg.className = 'promo-msg error';
                    promoMsg.textContent = data.error || 'Неверный промокод';
                    updateModalPrices();
                }
            } catch (err) {
                console.error("Promo check error:", err);
                promoMsg.className = 'promo-msg error';
                promoMsg.textContent = 'Ошибка проверки. Попробуйте позже.';
            }
        });
    }

    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            let nick = nickInput.value.trim();
            if (selectedPlatform === 'bedrock' && !nick.startsWith('.')) {
                nick = '.' + nick;
            }
            const server = document.getElementById('server-select').value;
            const submitBtn = document.getElementById('submit-pay-btn');
            const btnText = submitBtn.querySelector('.btn-text');
            const btnLoader = submitBtn.querySelector('.btn-loader');

            if (!nick || !selectedCheckoutItem) return;

            submitBtn.disabled = true;
            btnText.style.display = 'none';
            btnLoader.style.display = 'inline';

            const payload = {
                player_name: nick,
                item_id: selectedCheckoutItem.id,
                server_target: server,
                platform: selectedPlatform,
                promo_code: appliedPromo,
                custom_tokens: selectedCheckoutItem.custom_tokens || 0
            };

            try {
                const resp = await fetch('/api/create_payment', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                const data = await resp.json();
                if (data.success && data.payment_url) {
                    window.location.href = data.payment_url;
                } else {
                    alert(data.error || 'Ошибка при создании платежа');
                    submitBtn.disabled = false;
                    btnText.style.display = 'inline';
                    btnLoader.style.display = 'none';
                }
            } catch (err) {
                console.error(err);
                alert('Не удалось связаться с сервером платежей');
                submitBtn.disabled = false;
                btnText.style.display = 'inline';
                btnLoader.style.display = 'none';
            }
        });
    }
}

function openCheckoutModal(itemId) {
    let item = catalogItems.find(i => i.id === itemId);
    if (!item) {
        if (itemId === 'premium_30') item = { id: 'premium_30', name: 'Премиум на 30 дней', price: 99, badge: 'Подписка' };
        else if (itemId === 'premium_60') item = { id: 'premium_60', name: 'Премиум на 60 дней', price: 149, badge: 'Выгодно -25%' };
        else if (itemId === 'premium_90') item = { id: 'premium_90', name: 'Премиум на 90 дней', price: 249, badge: 'Хит -35%' };
        else if (itemId === 'building_pass') item = { id: 'building_pass', name: 'Building Pass (Мирное выживание)', price: 149, badge: 'Пропуск' };
        else if (itemId === 'hardcore_revive') item = { id: 'hardcore_revive', name: 'Возрождение на Хардкоре', price: 249, badge: 'Хардкор 1 Жизнь' };
        else if (itemId === 'unban') item = { id: 'unban', name: 'Разбан аккаунта', price: 149, badge: 'Услуга' };
        else if (itemId.startsWith('tokens_')) {
            const pkgMap = {
                tokens_1k: { name: '1 000 Токенов', price: 40 },
                tokens_5k: { name: '5 000 Токенов', price: 189 },
                tokens_15k: { name: '15 000 Токенов', price: 539 },
                tokens_30k: { name: '30 000 Токенов', price: 999 },
                tokens_50k: { name: '50 000 Токенов', price: 1549 },
                tokens_100k: { name: '100 000 Токенов', price: 2799 }
            };
            item = { id: itemId, name: pkgMap[itemId]?.name || 'Токены', price: pkgMap[itemId]?.price || 40, badge: 'Токены' };
        }
    }
    if (!item) return;

    selectedCheckoutItem = item;
    currentDiscount = 0;
    appliedPromo = "";

    document.getElementById('modal-item-name').textContent = item.name;
    document.getElementById('modal-item-badge').textContent = item.badge || 'Товар';
    document.getElementById('promo-code').value = '';
    document.getElementById('promo-msg').textContent = '';

    updateModalPrices();

    const modal = document.getElementById('checkout-modal');
    modal.classList.add('active');
}

function openCheckoutForCustomTokens(amountTokens) {
    const basePrice = amountTokens / BASE_TOKENS_PER_RUB;
    const progress = (amountTokens - 1000) / 99000.0;
    const discountPct = Math.round(progress * 30.0);
    const finalPrice = Math.max(10, Math.round(basePrice * (1 - discountPct / 100.0)));

    selectedCheckoutItem = {
        id: "custom_tokens",
        name: `${amountTokens.toLocaleString('ru-RU')} Токенов`,
        price: finalPrice,
        badge: discountPct > 0 ? `Скидка ${discountPct}%` : 'Токены',
        custom_tokens: amountTokens
    };

    currentDiscount = 0;
    appliedPromo = "";

    document.getElementById('modal-item-name').textContent = selectedCheckoutItem.name;
    document.getElementById('modal-item-badge').textContent = selectedCheckoutItem.badge;
    document.getElementById('promo-code').value = '';
    document.getElementById('promo-msg').textContent = '';

    updateModalPrices();

    const modal = document.getElementById('checkout-modal');
    modal.classList.add('active');
}

function updateModalPrices() {
    if (!selectedCheckoutItem) return;
    let price = selectedCheckoutItem.price;
    if (currentDiscount > 0) {
        price = Math.max(1, Math.round(price * (1 - currentDiscount / 100)));
    }
    document.getElementById('modal-item-price').textContent = `${price} ₽`;
    document.getElementById('summary-final-price').textContent = `${price} ₽`;
}

// 6. Token In-Game Purchase Instruction Modal
function initTokenInstructionModal() {
    const modal = document.getElementById('token-purchase-modal');
    const closeBtn = document.getElementById('token-modal-close-btn');
    const understandBtn = document.getElementById('close-token-inst-btn');

    const closeModal = () => modal.classList.remove('active');
    if (closeBtn) closeBtn.addEventListener('click', closeModal);
    if (understandBtn) understandBtn.addEventListener('click', closeModal);
}

function openTokenInstructionModal() {
    const modal = document.getElementById('token-purchase-modal');
    if (modal) modal.classList.add('active');
}

// 7. Load Catalog from Backend
async function loadCatalog() {
    try {
        const resp = await fetch('/api/catalog');
        const data = await resp.json();
        if (data.success && data.items) {
            catalogItems = data.items;
        }
    } catch (e) {
        console.warn('Using local fallback catalog data');
    }
}

// 8. Recent Donates Live Feed
async function loadRecentDonates() {
    try {
        const resp = await fetch('/api/recent_donates');
        const data = await resp.json();
        const ticker = document.getElementById('feed-ticker');
        if (data.success && data.donations && data.donations.length > 0) {
            ticker.innerHTML = data.donations.map(d => `
                <span class="feed-item">
                    <strong>${d.player_name}</strong> приобрел <strong>${d.item_name}</strong> (${d.amount} ₽)
                </span>
            `).join(' • ');
        } else {
            ticker.innerHTML = '<span class="feed-item">Будьте первым, кто поддержит сервер сегодня!</span>';
        }
    } catch (e) {
        console.error('Failed to load live feed:', e);
    }
}

// Inline Promo Code Logic
window.applyInlinePromo = async function(section) {
    const input = document.getElementById(`inline-promo-${section}`);
    const msg = document.getElementById(`inline-promo-msg-${section}`);
    if (!input || !msg) return;

    const code = input.value.trim().toUpperCase();
    if (!code) {
        msg.textContent = 'Введите код';
        msg.style.display = 'block';
        msg.style.color = '#eb4d4b';
        return;
    }

    try {
        const resp = await fetch(`/api/check_promo?code=${encodeURIComponent(code)}`);
        const data = await resp.json();

        if (data.success) {
            currentDiscount = data.discount_percent;
            appliedPromo = code;
            
            // Sync with modal if opened later
            const modalInput = document.getElementById('promo-code');
            const modalMsg = document.getElementById('promo-msg');
            if (modalInput) modalInput.value = code;
            if (modalMsg) {
                modalMsg.className = 'promo-msg success';
                modalMsg.textContent = `✓ Промокод применен: скидка ${currentDiscount}%!`;
            }

            msg.textContent = `✓ Успешно! Скидка ${currentDiscount}%`;
            msg.style.color = '#6ab04c';
            msg.style.display = 'block';

            // Trigger updates on the page
            updatePremiumCta();
            if (document.getElementById('tokens-range-slider')) {
                // To trigger calculator update, just dispatch input event
                document.getElementById('tokens-range-slider').dispatchEvent(new Event('input'));
            }
        } else {
            currentDiscount = 0;
            appliedPromo = null;
            msg.textContent = data.error || 'Неверный код';
            msg.style.color = '#eb4d4b';
            msg.style.display = 'block';
            updatePremiumCta();
            if (document.getElementById('tokens-range-slider')) {
                document.getElementById('tokens-range-slider').dispatchEvent(new Event('input'));
            }
        }
    } catch (err) {
        msg.textContent = 'Ошибка соединения';
        msg.style.color = '#eb4d4b';
        msg.style.display = 'block';
    }
};

// 9. Check URL for payment return
function checkUrlParams() {
    const params = new URLSearchParams(window.location.search);
    if (params.get('success') === '1') {
        const successModal = document.getElementById('success-modal');
        const closeBtn = document.getElementById('success-close-btn');
        const finishBtn = document.getElementById('finish-success-btn');

        const closeModal = () => {
            successModal.classList.remove('active');
            window.history.replaceState({}, document.title, '/');
        };

        if (closeBtn) closeBtn.addEventListener('click', closeModal);
        if (finishBtn) finishBtn.addEventListener('click', closeModal);

        if (successModal) successModal.classList.add('active');
    }
}
