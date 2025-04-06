// Cart functionality
document.addEventListener('DOMContentLoaded', function() {
    // Initialize cart if it doesn't exist
    if (!localStorage.getItem('cart')) {
        localStorage.setItem('cart', JSON.stringify([]));
    }
    
    // Add event listeners to all "Add to cart" buttons on the main page
    const addToCartButtons = document.querySelectorAll('.product a button');
    addToCartButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Get product information from the parent elements
            const productElement = this.closest('.product');
            const productName = productElement.querySelector('p').textContent;
            const productPrice = productElement.querySelector('.price').textContent;
            const productImage = productElement.querySelector('img').src;
            const productId = productImage.split('/').pop().split('.')[0];
            
            // Add product to cart
            addToCart({
                id: productId,
                name: productName,
                price: productPrice,
                image: productImage,
                quantity: 1
            });
            
            // Show confirmation message
            alert('Product added to cart!');
        });
    });
    
    // If on payment page, display cart items
    if (document.querySelector('.CartPageContainer')) {
        displayCartItems();
    }
});

// Function to add product to cart
function addToCart(product) {
    let cart = JSON.parse(localStorage.getItem('cart'));
    
    // Check if product already exists in cart
    const existingProductIndex = cart.findIndex(item => item.id === product.id);
    
    if (existingProductIndex !== -1) {
        // If product exists, increase quantity
        cart[existingProductIndex].quantity += product.quantity;
    } else {
        // If product doesn't exist, add it to cart
        cart.push(product);
    }
    
    // Save updated cart to localStorage
    localStorage.setItem('cart', JSON.stringify(cart));
}

// Function to display cart items on payment page
function displayCartItems() {
    const cart = JSON.parse(localStorage.getItem('cart'));
    const productContainer = document.querySelector('.product-container');
    
    // Clear existing products
    productContainer.innerHTML = '';
    
    // If cart is empty, show message
    if (cart.length === 0) {
        productContainer.innerHTML = '<p>Your cart is empty. Add products from the main page.</p>';
        return;
    }
    
    // Display each product in cart
    cart.forEach(product => {
        const productElement = document.createElement('div');
        productElement.className = 'bbbbbb';
        productElement.dataset.price = product.price.replace(/[^\d]/g, '');
        
        productElement.innerHTML = `
            <img src="${product.image}" alt="${product.name}">
            <h5>${product.name}</h5>
            <p>Giá: ${product.price}</p>
            <div class="quantity-control">
                <button onclick="updateQuantity('${product.id}', -1)">-</button>
                <input type="text" value="${product.quantity}" readonly>
                <button onclick="updateQuantity('${product.id}', 1)">+</button>
            </div>
        `;
        
        productContainer.appendChild(productElement);
    });
    
    // Update total price
    updateTotalPrice();
}

// Function to update product quantity
function updateQuantity(productId, change) {
    let cart = JSON.parse(localStorage.getItem('cart'));
    const productIndex = cart.findIndex(item => item.id === productId);
    
    if (productIndex !== -1) {
        cart[productIndex].quantity += change;
        
        // Remove product if quantity is 0 or less
        if (cart[productIndex].quantity <= 0) {
            cart.splice(productIndex, 1);
        }
        
        // Save updated cart
        localStorage.setItem('cart', JSON.stringify(cart));
        
        // Refresh display
        displayCartItems();
    }
}

// Function to update total price
function updateTotalPrice() {
    const cart = JSON.parse(localStorage.getItem('cart'));
    let total = 0;
    
    cart.forEach(product => {
        const price = parseInt(product.price.replace(/[^\d]/g, ''));
        total += price * product.quantity;
    });
    
    // Format total price with commas for thousands
    const formattedTotal = total.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    document.getElementById('total-price').textContent = `${formattedTotal}đ`;
}

// Function to clear cart
function clearCart() {
    localStorage.setItem('cart', JSON.stringify([]));
    displayCartItems();
    // Reset the total price to 0
    document.getElementById('total-price').textContent = '0đ';
} 

// Get product details from page
function getProductDetailsFromPage() {
    const productName = document.querySelector('.product-details h1')?.textContent.trim();
    const currentPriceText = document.querySelector('.current-price')?.textContent.trim();
    const originalPriceText = document.querySelector('.original-price')?.textContent.trim();
    const discountText = document.querySelector('.discount')?.textContent.trim();
    const quantityInput = document.querySelector('input[name="quantity"]');

    // Get the correct quantity based on user input
    let quantity = 1;
    if (quantityInput) {
        const val = quantityInput.value.trim();
        if (val !== '' && !isNaN(val)) {
            quantity = parseInt(val);
        }
    }

    const productImage = document.getElementById('main-image')?.src;
    const productId = productImage ? productImage.split('/').pop().split('.')[0] : 'unknown';

    return {
        id: productId,
        name: productName,
        price: currentPriceText,
        originalPrice: originalPriceText,
        discount: discountText,
        image: productImage,
        quantity: quantity
    };
}

document.addEventListener('DOMContentLoaded', function () {
    const addToCartBtn = document.querySelector('.add-to-cart');

    if (addToCartBtn) {
        addToCartBtn.addEventListener('click', function (e) {
            e.preventDefault();

            const product = getProductDetailsFromPage();
            console.log('Thông tin sản phẩm:', product); // Debug nếu cần
            addToCart(product);
            alert("Sản phẩm đã được thêm vào giỏ hàng!");
        });
    }
});
