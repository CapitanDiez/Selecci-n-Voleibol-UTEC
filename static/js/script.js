// Gestor de Voleibol - JavaScript vanilla

// Vista previa de la tarjeta en Agregar jugador
document.addEventListener("DOMContentLoaded", function () {
    const formulario = document.getElementById("form-jugador");
    if (!formulario) {
        return;
    }

    const enlaces = [
        ["nombre", "previa-nombre", "NUEVO JUGADOR"],
        ["matricula", "previa-matricula", "———"],
        ["rama", "previa-rama", "—"],
        ["numero_playera", "previa-numero", "00"],
    ];

    function actualizarPrevia() {
        enlaces.forEach(function (enlace) {
            const campo = document.getElementById(enlace[0]);
            const destino = document.getElementById(enlace[1]);
            let valor = campo.value.trim();
            if (campo.tagName === "SELECT" && valor !== "") {
                valor = campo.options[campo.selectedIndex].text;
            }
            destino.textContent = valor !== "" ? valor : enlace[2];
        });
    }

    formulario.addEventListener("input", actualizarPrevia);
    formulario.addEventListener("change", actualizarPrevia);
    actualizarPrevia();

    // Muestra la foto elegida antes de guardarla
    const foto = document.getElementById("foto");
    const imagen = document.getElementById("previa-foto");
    foto.addEventListener("change", function () {
        if (foto.files.length > 0) {
            imagen.src = URL.createObjectURL(foto.files[0]);
        }
    });
});
