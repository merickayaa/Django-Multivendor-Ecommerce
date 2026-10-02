$(document).on("click", "#add-to-cart-btn", function () {
    let this_val = $(this)
    let parentCard = this_val.closest(".card-body");
    let quantity = parentCard.find(".product-quantity").val();
    let product_title = parentCard.find(".product-title").val();
    let product_id = parentCard.find(".product-id").val();
    let product_price = parentCard.find(".current-product-price").text();
    let product_pid = parentCard.find(".product-pid").val();
    let product_image = parentCard.find(".product-image").val();
    let product_vendor = parentCard.find(".product-vendor").val();
    console.log("Quantity:", quantity);
    console.log("parentCard:", parentCard);
    console.log("Title:", product_title);
    console.log("Price:", product_price);
    console.log("ID:", product_id);
    console.log("PID:", product_pid);
    console.log("IMG:", product_image);
    console.log("Vendor:", product_vendor);
    console.log("this_val:", this_val);

    console.log("Current Element:", this_val);
    $.ajax({
        url: '/add-to-cart/',
        type: 'POST',
        data: {
            'id':product_id,
            'pid':product_pid,
            'image': product_image,
            'qty':quantity,
            'title': product_title,
            'price': product_price,
            'vendor': product_vendor
        },
        dataType:'json',
        beforeSend:function(){
            console.log("Adding Product to Cart")
        },
        success: function(response){
            console.log(response);
            this_val.html("✓")
            console.log("Added Product to Cart")
            $(".cart-items-count").text(response.totalcartitems)
        }
    })
});

$(document).on("click", "#add-to-cart-btn-detail", function () {
    let this_val = $(this)
    let parentCard = this_val.closest(".wrapped");
    let quantity = parentCard.find(".product-quantity").val();
    let product_title = parentCard.find(".product-title").val();
    let product_id = parentCard.find(".product-id").val();
    let product_price = parentCard.find(".current-product-price").val();
    let product_pid = parentCard.find(".product-pid").val();
    let product_image = parentCard.find(".product-image").val();
    let product_vendor = parentCard.find(".product-vendor").val();
    console.log("Quantity:", quantity);
    console.log("parentCard:", parentCard);
    console.log("Title:", product_title);
    console.log("Price:", product_price);
    console.log("ID:", product_id);
    console.log("PID:", product_pid);
    console.log("IMG:", product_image);
    console.log("Vendor:", product_vendor);
    console.log("this_val:", this_val);

    console.log("Current Element:", this_val);
    $.ajax({
        url: '/add-to-cart/',
        type: 'POST',
        data: {
            'pid':product_pid,
            'image': product_image,
            'qty':quantity,
            'title': product_title,
            'price': product_price,
            'vendor': product_vendor
        },
        dataType:'json',
        beforeSend:function(){
            console.log("Adding Product to Cart")
        },
        success: function(response){
            console.log(response);
            this_val.html("✓")
            console.log("Added Product to Cart")
            $(".cart-items-count").text(response.totalcartitems)
        },error: function(response){
            console.log(response)
            console.log("Not Added Product to Cart")
        }
    })
});

$(document).on("click", ".increase-btn, .decrease-btn", function () {
    let parentRow = $(this).closest(".card");
    let ParentRow = $(this).closest(".cart");
    let quantityElement = parentRow.find(".quantity");
    let currentQty = parseInt(quantityElement.text());
    let newQty = $(this).hasClass("increase-btn") ? currentQty + 1 : currentQty - 1;
    let productId = parentRow.find(".product-pid").val();
    
    if (newQty >= 0) {
        $.ajax({
            url: '/update-cart-item/',
            type: 'POST',
            data: {
                'pid': productId,
                'qty': newQty
            },
            dataType: 'json',
            success: function (response) {
                if (response.success) {
                    console.log("Sepet güncellendi:", response);
                    if (response.is_empty) {
                        window.location.href = "/";
                    }
                    // Yeni miktarı DOM'da güncelle
                    quantityElement.text(newQty);

                    // Ürün fiyatını güncelle
                    if (response.cart_data && response.cart_data[productId]) {
                        let price = parseFloat(response.cart_data[productId].price);
                        let productTotalElement = parentRow.find(".product-total");

                        // Miktar ve fiyat çarpımını hesaplayıp DOM'da göster
                        productTotalElement.text(`₺${(price * newQty).toFixed(2)}`);
                    } else {
                        console.error("Ürün verisi bulunamadı");
                    }

                    // Sepet toplamını güncelle
                    $(".cart-total-amount").text(`₺${response.cart_total_amount.toFixed(2)}`);
                    $(".cart-items-count").text(response.totalcartitems);

                    // Sepetteki ürünlerin toplamını canlı olarak güncelle
                    $.each(response.cart_data, function(productId, itemData) {
                        // Her bir ürün için miktar ve toplam fiyatı güncelle
                        $(`#product-${productId}`).find('.product-total').text(`₺${(itemData.price * itemData.qty).toFixed(2)}`);
                        $(`#product-${productId}`).find('.quantity').text(itemData.qty);
                    });
                    

                    // Miktar 0 olduğunda ürünü DOM'dan kaldır
                    if (newQty === 0) {
                        ParentRow.remove();  // Sepetten ürünü kaldır {
                        // Her bir ürün için miktar ve toplam fiyatı güncelle
                        $(`#product-${productId}`).remove()

                    }
                } else {
                    console.error("Sepet güncellenirken hata oluştu:", response.error);
                }
            },
            error: function (xhr) {
                console.error("Hata:", xhr.responseText);
            }
        });
    }
});





$(document).on("click", ".increase-btn-detail, .decrease-btn-detail", function () {
    let this_val = $(this);
    let parentRow = this_val.closest(".wrapped");
    let quantityElement = parentRow.find(".quantity");
    let currentQty = parseInt(quantityElement.text());
    let newQty = $(this).hasClass("increase-btn-detail") ? currentQty + 1 : (currentQty > 1 ? currentQty - 1 : 1); // Miktar 1'den küçük olmasın
    let productId = parentRow.find(".product-pid").val();
    let productTitle = parentRow.find(".product-title").val();
    let productPrice = parentRow.find(".current-product-price").val();
    let productImage = parentRow.find(".product-image").val();
    let productVendor = parentRow.find(".product-vendor").val();

    if (newQty >= 1) {
        quantityElement.text(newQty);
    }

    // Sepete eklemek için Butona Tıklama
    $(document).on("click", "#add-to-cart-btn-detail", function () {
        let this_val = $(this)
        let parentCard = this_val.closest(".wrapped");
        let quantity = parentCard.find(".product-quantity").val();
        let product_title = parentCard.find(".product-title").val();
        let product_id = parentCard.find(".product-id").val();
        let product_price = parentCard.find(".current-product-price").val();
        let product_pid = parentCard.find(".product-pid").val();
        let product_image = parentCard.find(".product-image").val();
        let product_vendor = parentCard.find(".product-vendor").val();
        console.log("Quantity:", quantity);
        console.log("parentCard:", parentCard);
        console.log("Title:", product_title);
        console.log("Price:", product_price);
        console.log("ID:", product_id);
        console.log("PID:", product_pid);
        console.log("IMG:", product_image);
        console.log("Vendor:", product_vendor);
        console.log("this_val:", this_val);

        console.log("Current Element:", this_val);
        $.ajax({
            url: '/add-to-cart/',
            type: 'POST',
            data: {
                'id':product_id,
                'pid':product_pid,
                'image': product_image,
                'qty':quantity,
                'title': product_title,
                'price': product_price,
                'vendor': product_vendor
            },
            dataType:'json',
            beforeSend:function(){
                console.log("Adding Product to Cart")
            },
            success: function(response){
                console.log(response);
                this_val.html("✓")
                console.log("Added Product to Cart")
                $(".cart-items-count").text(response.totalcartitems)
            }
        })
    });
});


$(document).on("click", ".make-default-address", function(){
    let id = $(this).attr("data-address-id")
    let this_val = $(this)
    console.log("id ", id)
    console.log("element: ", this_val)

    $.ajax({
        url: '/make-default-address/',
        type:"POST",
        data: {
            "id":id,
        },
        dataType:"json",
        success: function(response){
            console.log("Address Made Default")
            if (response.boolean == true){
                $(".check").hide();  // Tüm tikleri gizle
                $(".action_btn").show();  // Tüm butonları göster
                $(".check" + id).show();  // Tıklanan adresin tikini göster
                $(".button" + id).hide();  // Tıklanan adresin butonunu gizle

                $(".make-default-address").each(function() {
                    var otherId = $(this).data('address-id');
                    if (otherId != id) {
                        $(".check" + otherId).hide();
                        $(".button" + otherId).show();
                    }
                });
            }
        }
    })

});

$(document).on("click", ".delete-address", function(){
    let id = $(this).attr("data-address-id")
    let this_val = $(this)
    console.log("id ", id)
    console.log("element: ", this_val)

    $.ajax({
        url: '/delete-address/',
        type:"POST",
        data: {
            "id":id,
        },
        dataType:"json",
        success: function(response){
            console.log("Address Deleted")
            if (response.boolean == true){
                $(".address"+id).hide()
            }
        }
    })

});

$(document).on("click", ".add-to-wishlist", function (){
    let product_id = $(this).attr("data-product-item")
    let this_val = $(this)
    let parentSpan = this_val.closest("span")
    let average_rating = parentSpan.find(".product-rating").val()
    console.log("product_id: ",product_id)
    console.log("this_val: ",this_val)

    $.ajax({
        url: "/add-to-wishlist/",
        type:"POST",
        data: { 
            "id": product_id,
            "average_rating": average_rating
         },
        dataType: "json",
        beforeSend: function () {
            this_val.html("❤︎");
        },
        success: function (response) {
            if (response.bool === true) {
                console.log("Added to wishlist");
            }
        },
        error: function (xhr, status, error) {
            console.error("Error: ", error);
            console.log("Response: ", xhr.responseText);
        }
    });
})

$(document).on("click", ".delete-wishlist-product", function () {
    const productId = $(this).data("wishlist-product");

    $.ajax({
        url: "/remove-to-wishlist/",
        type:"POST",
        data: { id: productId },
        dataType: "json",
        success: function (response) {
            if (response.bool === true) {
                // Yalnızca wishlist kısmını güncelle
                $("#wishlist-list").html(response.wishlist_html);
            }
        },
        error: function () {
            alert("An error occurred while removing the product.");
        }
    });
});


$(document).on("submit", "#contact_form_ajax", function (e){
    e.preventDefault()
    console.log("Submitted");

    let full_name = $("#full_name").val()
    let email = $("#email").val()
    let phone = $("#phone").val()
    let subject = $("#subject").val()
    let message = $("#message").val()

    console.log("Name: ", full_name);
    console.log("Email: ", email);
    console.log("phone: ", phone);
    console.log("subject: ", subject);
    console.log("message: ", message);

    $.ajax({
        url:"/ajax-contact-form/",
        type:"POST",
        data: {
            "full_name":full_name,
            "email":email,
            "phone":phone,
            "subject":subject,
            "message":message,
        },
        dataType:"json",
        beforeSend: function () {
            console.log("Sending");
        },
        success: function (res){
            console.log("Sent");
            $("#sendUs").hide()
            $("#contact_form_ajax").hide()
            $("#message-response").html("Message Sent")
            
        }
    })

})


function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie('csrftoken');

$.ajaxSetup({
    headers: { "X-CSRFToken": csrftoken }
});