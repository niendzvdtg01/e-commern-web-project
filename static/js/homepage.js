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

function searchProduct() {
    let query = document.getElementById("search").value.trim();
    let popup = document.getElementById("search-result");

    if (query.length === 0) {
        popup.classList.remove("active");
        document.getElementById("result-body").innerHTML = "";
        return;
    } else {
        popup.classList.add("active");
    }

    fetch(`/search?q=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            console.log("Dữ liệu nhận được:", data);
            let resultHTML = "";
            data.forEach(row => {
                resultHTML += `<tr>
                    <td>${row[0]}</td>
                    <td>${row[1]}</td>
                    <td>${row[2]}</td>
                </tr>`;
            });
            document.getElementById("result-body").innerHTML = resultHTML;
        })
        .catch(error => console.error("❌ Lỗi API:", error));
}




