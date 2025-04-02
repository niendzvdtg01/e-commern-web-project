function openpopup(){
    document.getElementById("loginPopup").style.display="block";
}
function closepopup(){
    document.getElementById("loginPopup").style.display="none";
}

function opensearch() {
    let popup = document.getElementById("search-popup");
    if (popup) {
        popup.style.display = "block";
        setTimeout(() => {
            popup.classList.add("active");
        }, 10);
    } else {
        console.error("Không tìm thấy phần tử có ID 'search-popup'");
    }
}

function closesearch() {
    let popup = document.getElementById("search-popup");
    popup.classList.remove("active");
    setTimeout(() => {
        popup.style.display = "none"; // Ẩn sau khi hiệu ứng kết thúc
    }, 300); // Đợi transition hoàn thành (0.3s)
}

let searchTimeout;
function searchProduct() {
    clearTimeout(searchTimeout); // Xóa bỏ timeout cũ nếu có
    searchTimeout = setTimeout(() => {
        let query = document.getElementById("search").value.trim();
        let popup = document.getElementById("search-result");
        let resultBody = document.getElementById("result-body");

        if (query.length === 0) {
            popup.classList.remove("active");
            resultBody.innerHTML = "";
            return;
        } else {
            popup.classList.add("active");
            resultBody.innerHTML = `<tr><td colspan="3">Đang tìm kiếm...</td></tr>`; // Thêm loading
        }

        fetch(`/search?q=${encodeURIComponent(query)}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (Array.isArray(data) && data.length > 0) {
                    renderResults(data);
                } else {
                    resultBody.innerHTML = `<tr><td colspan="3">Không tìm thấy sản phẩm</td></tr>`;
                }
            })
            .catch(error => {
                console.error("❌ Lỗi API:", error);
                resultBody.innerHTML = `<tr><td colspan="3">Lỗi khi tải dữ liệu</td></tr>`;
            });

    }, 300); // Debounce 300ms để tránh spam request
}

function renderResults(data) {
    let resultHTML = data.map(row => `
        <a href="#">
                    <img src="/static/pictures/${row.product_id}.png" alt="">
                        <div>
                            <p>${row.product_name ?? "N/A"}</p>
                            <p>⭐⭐⭐⭐⭐</p>
                            <p style="font-weight: bold; color: red;">${row.price ?? "N/A"}</p>
                        </div>
        </a>
    `).join("");

    document.getElementById("result-body").innerHTML = resultHTML;
}