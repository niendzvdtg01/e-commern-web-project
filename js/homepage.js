function openpopup(){
    document.getElementById("loginPopup").style.display="block";
}
function closepopup(){
    document.getElementById("loginPopup").style.display="none";
}
function opensearch() {
    let popup = document.getElementById("search-popup");
    popup.style.display = "block"; // Hiển thị popup trước khi thêm hiệu ứng
    setTimeout(() => {
        popup.classList.add("active");
    }, 10); // Delay nhỏ để hiệu ứng hoạt động
}

function closesearch() {
    let popup = document.getElementById("search-popup");
    popup.classList.remove("active");
    setTimeout(() => {
        popup.style.display = "none"; // Ẩn sau khi hiệu ứng kết thúc
    }, 300); // Đợi transition hoàn thành (0.3s)
}
