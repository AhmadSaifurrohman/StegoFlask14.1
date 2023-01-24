function decode() {
    const activeEncode = document.getElementById("encode")
    activeEncode.classList.remove("active")
    const encodeMenu = document.getElementById("encodeMenu")
    encodeMenu.style.display = "none"

    const activeDecode = document.getElementById("decode")
    activeDecode.classList.add("active")
    const decodeMenu = document.getElementById("decodeMenu")
    decodeMenu.style.display = "block"
}

function encode() {
    const activeDecode = document.getElementById("decode")
    activeDecode.classList.remove("active")
    const decodeMenu = document.getElementById("decodeMenu")
    decodeMenu.style.display = "none"

    const activeEncode = document.getElementById("encode")
    activeEncode.classList.add("active")
    const encodeMenu = document.getElementById("encodeMenu")
    encodeMenu.style.display = "block"
}

function submitFormDecrypt() {
    document.getElementById("formDecrypt").submit();
    event.preventDefault();
}


