document.addEventListener('DOMContentLoaded', function() {
    // Handle all add to cart forms
    document.querySelectorAll('.add-to-cart-form').forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const productId = formData.get('product_id');
            const messageDiv = document.getElementById(`cart-message-${productId}`);
            
            fetch('/add-to-cart', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    messageDiv.textContent = data.message;
                    messageDiv.style.display = 'block';
                    messageDiv.style.color = 'green';
                    
                    // Update cart count in header if it exists
                    const cartCount = document.getElementById('cart-count');
                    if (cartCount) {
                        cartCount.textContent = data.cart_count;
                    }
                    
                    // Hide message after 3 seconds
                    setTimeout(() => {
                        messageDiv.style.display = 'none';
                    }, 3000);
                } else {
                    messageDiv.textContent = data.message;
                    messageDiv.style.display = 'block';
                    messageDiv.style.color = 'red';
                    
                    // Hide message after 3 seconds
                    setTimeout(() => {
                        messageDiv.style.display = 'none';
                    }, 3000);
                }
            })
            .catch(error => {
                messageDiv.textContent = 'Có lỗi xảy ra, vui lòng thử lại';
                messageDiv.style.display = 'block';
                messageDiv.style.color = 'red';
                
                setTimeout(() => {
                    messageDiv.style.display = 'none';
                }, 3000);
            });
        });
    });
});
function updateQuantity(productId, change) {
    const quantityInput = document.getElementById(`quantity-${productId}`);
    const currentQuantity = parseInt(quantityInput.value);
    const newQuantity = currentQuantity + change;
    
    if (newQuantity >= 0) {
        if (newQuantity === 0) {
            // If quantity becomes 0, remove the item
            removeFromCart(productId);
        } else {
            // Get the product element and its details
            const productElement = document.querySelector(`[data-product-id="${productId}"]`);
            const priceText = productElement.querySelector('p').textContent;
            const price = parseInt(priceText.replace('Giá: ', '').replace('đ', ''));
            
            // Create form data
            const formData = new FormData();
            formData.append('product_id', productId);
            formData.append('quantity', newQuantity);
            formData.append('price', price);
            
            // Send POST request
            fetch('/update-cart', {
                method: 'POST',
                body: formData
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    // Update quantity input
                    quantityInput.value = newQuantity;
                    
                    // Update total price
                    const totalElement = document.getElementById('total-price');
                    if (totalElement) {
                        totalElement.textContent = data.total + 'đ';
                    }
                    
                    // Update cart count in header if it exists
                    const cartCount = document.getElementById('cart-count');
                    if (cartCount) {
                        cartCount.textContent = data.cart_count;
                    }
                } else {
                    console.error('Failed to update cart:', data.message);
                }
            })
            .catch(error => {
                console.error('Error updating cart:', error);
                // Revert the quantity if the update failed
                quantityInput.value = currentQuantity;
            });
        }
    }
}

function removeFromCart(productId) {
    // Create form data
    const formData = new FormData();
    formData.append('product_id', productId);
    
    fetch('/remove-from-cart', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            // Remove the product element from the DOM
            const productElement = document.querySelector(`[data-product-id="${productId}"]`);
            if (productElement) {
                productElement.remove();
            }
            
            // Update total price
            const totalElement = document.getElementById('total-price');
            if (totalElement) {
                totalElement.textContent = data.total + 'đ';
            }
            
            // If cart is empty, show empty cart message
            if (data.cart_count === 0) {
                const productContainer = document.querySelector('.product-container');
                if (productContainer) {
                    productContainer.innerHTML = '<div class="empty-cart-message"><p>Giỏ hàng của bạn đang trống</p></div>';
                }
            }
        } else {
            console.error('Failed to remove item:', data.message);
        }
    })
    .catch(error => {
        console.error('Error removing item:', error);
    });
}

function clearCart() {
    fetch('/clear-cart', {
        method: 'POST'
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            const productContainer = document.querySelector('.product-container');
            if (productContainer) {
                productContainer.innerHTML = '<div class="empty-cart-message"><p>Giỏ hàng của bạn đang trống</p></div>';
            }
            const totalElement = document.getElementById('total-price');
            if (totalElement) {
                totalElement.textContent = '0đ';
            }
        } else {
            console.error('Failed to clear cart:', data.message);
        }
    })
    .catch(error => {
        console.error('Error clearing cart:', error);
    });
}

function createPayment() {
    // Get cart items
    const cartItems = Array.from(document.querySelectorAll('.data-container')).map(item => ({
        product_id: item.dataset.productId,
        name: item.querySelector('h3').textContent,
        price: parseInt(item.querySelector('p').textContent.replace('Giá: ', '').replace('đ', '')),
        quantity: parseInt(item.querySelector('input[type="number"]').value)
    }));

    // Get total amount
    const total = parseInt(document.getElementById('total-price').textContent.replace('đ', ''));

    // Send payment request
    fetch('/create-payment', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        },
        body: JSON.stringify({
            item: cartItems,
            total: total
        })
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(data => {
                throw new Error(data.message || 'Payment creation failed');
            });
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            // Store app_trans_id in sessionStorage
            sessionStorage.setItem('app_trans_id', data.app_trans_id);
            // Redirect to payment URL
            window.location.href = data.payment_url;
        } else {
            alert(data.message || 'Payment creation failed');
        }
    })
    .catch(error => {
        console.error('Error creating payment:', error);
        alert(error.message || 'Có lỗi xảy ra khi tạo thanh toán. Vui lòng thử lại.');
    });
} 