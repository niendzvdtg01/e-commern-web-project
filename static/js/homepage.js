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

document.addEventListener("DOMContentLoaded", function () {
    let searchInput = document.getElementById("search");
    let popup = document.getElementById("search-result");

    if (!searchInput || !popup) {
        console.error("Không tìm thấy phần tử cần thiết!");
        return;
    }

    searchInput.oninput = function () {
        console.log("Text nhập:", this.value);

        if (this.value.trim() !== "") {
            popup.classList.add("active"); // Hiển thị bảng
        } else {
            popup.classList.remove("active"); // Ẩn bảng
        }
    };
});