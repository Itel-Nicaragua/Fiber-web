document.addEventListener("DOMContentLoaded", function () {
  // Cache de elementos DOM
  const searchInput = document.querySelector('input[name="search"]');
  const searchForm = document.querySelector('form[method="get"]');
  const clearBtn = document.querySelector(".btn-outline-secondary");
  const filtroHidden = document.getElementById("filtro_fecha_hidden");
  const filtroRadios = document.querySelectorAll(
    'input[name="filtro_fecha_radio"]'
  );

  filtroRadios.forEach((radio) => {
    radio.addEventListener("change", () => {
      if (radio.value === "") {
        filtroHidden.removeAttribute("name"); // No se envía el campo
        filtroHidden.value = "";
      } else {
        filtroHidden.setAttribute("name", "filtro_fecha");
        filtroHidden.value = radio.value;
      }
      searchForm.submit();
    });
  });

  // Establecer el estado inicial del campo oculto
  const selectedRadio = document.querySelector(
    'input[name="filtro_fecha_radio"]:checked'
  );
  if (!selectedRadio || selectedRadio.value === "") {
    filtroHidden.removeAttribute("name"); // No enviar si no hay selección
  } else {
    filtroHidden.setAttribute("name", "filtro_fecha");
    filtroHidden.value = selectedRadio.value;
  }

  // Variables para control de búsqueda
  let searchTimeout = null;
  let lastSearchValue = "";
  const DEBOUNCE_DELAY = 400; // ms

  // Optimización: Evitar múltiples submits innecesarios
  const handleSearch = function () {
    const currentValue = searchInput.value.trim();

    // No hacer nada si el valor no ha cambiado
    if (currentValue === lastSearchValue) return;

    lastSearchValue = currentValue;

    // Solo buscar si hay al menos 3 caracteres o está vacío (reset)
    if (currentValue.length === 0 || currentValue.length >= 3) {
      searchForm.submit();
    }
  };

  // Agregar evento de input para búsqueda con debounce
  searchInput.addEventListener("input", () => {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(handleSearch, DEBOUNCE_DELAY);
  });

  // Manejar el botón de limpiar
  if (clearBtn) {
    clearBtn.addEventListener("click", () => {
      searchInput.value = "";
      filtroRadios.forEach((radio) => (radio.checked = false));
      filtroHidden.removeAttribute("name");
      filtroHidden.value = "";
      searchForm.submit();
    });
  }
});

const loadingModal = document.getElementById("loadingModal");
loadingModal.classList.remove("hidden");

// Hide loading modal after 500ms
setTimeout(() => {
  loadingModal.classList.add("hidden");
}, 500);

// Info cliente
document.addEventListener("DOMContentLoaded", function () {
  const tabButtons = document.querySelectorAll(".tab-btn");
  const tabContents = document.querySelectorAll(".tab-content");

  // Al cargar: seleccionar el tab1 por defecto
  const defaultTab = "tab1";
  tabContents.forEach((content) => {
    content.classList.add("hidden");
  });
  document.getElementById(defaultTab).classList.remove("hidden");

  tabButtons.forEach((btn) => {
    if (btn.getAttribute("data-tab") === defaultTab) {
      btn.classList.add("bg-blue-900", "text-white");
    } else {
      btn.classList.remove("bg-blue-900", "text-white");
    }
  });

  // Manejadores de clic
  tabButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const tabId = button.getAttribute("data-tab");

      tabContents.forEach((content) => content.classList.add("hidden"));
      document.getElementById(tabId).classList.remove("hidden");

      tabButtons.forEach((btn) =>
        btn.classList.remove("bg-blue-900", "text-white")
      );
      button.classList.add("bg-blue-900", "text-white");
    });
    document
      .getElementById("tabs-wrapper")
      .scrollTo({ top: 0, behavior: "auto" });
  });
});

const btns = document.querySelectorAll(".tab-btn");
const tabs = document.querySelectorAll(".tab-content");

btns.forEach((btn) => {
  btn.addEventListener("click", () => {
    const showId = btn.getAttribute("data-tab");
    tabs.forEach((tab) => {
      tab.id === showId
        ? tab.classList.replace("hidden", "block")
        : tab.classList.replace("block", "hidden");
    });
  });
});

// Opciones de estado

document.addEventListener("DOMContentLoaded", function () {
  const nextBtn = document.querySelector('[data-modal-target="second-modal"]');
  const selectedSpan = document.getElementById("selected-option");

  nextBtn.addEventListener("click", function () {
    const selectedRadio = document.querySelector(
      'input[name="estado"]:checked'
    );
    if (selectedRadio) {
      selectedSpan.textContent = selectedRadio.value;
    } else {
      selectedSpan.textContent = "Ninguna opción seleccionada";
    }
  });
});

document.querySelectorAll('input[name="estado"]').forEach((radio) => {
  radio.addEventListener("change", function () {
    document.getElementById("selected-option").textContent = this.value;
  });
});

document.addEventListener('DOMContentLoaded', function() {
  var elems = document.querySelectorAll('.datepicker');
  M.Datepicker.init(elems, {
    format: 'dd-mm-yyyy'
  });
});


document.addEventListener("DOMContentLoaded", function () {
  const form = document.querySelector("#crud-modal form");
  const submitButton = form.querySelector('button[type="submit"]');

  const showInfoToast = async (mensaje) => {
    const Toast = Swal.mixin({
      toast: true,
      position: "top-end",
      showConfirmButton: false,
      timer: 2000,
      timerProgressBar: true,
      icon: "info",
      didOpen: (toast) => {
        toast.addEventListener("mouseenter", Swal.stopTimer);
        toast.addEventListener("mouseleave", Swal.resumeTimer);
      },
    });

    await Toast.fire({ title: mensaje });
  };

  let formSubmitting = false; // bandera para evitar múltiples envíos

  submitButton.addEventListener("click", async function (event) {
    event.preventDefault();

    if (formSubmitting) return; // si ya se está enviando, no hacer nada

    submitButton.disabled = true;

    const herramientaCobro = form.querySelector('input[name="herramienta_cobro"]:checked');
    if (!herramientaCobro) {
      await showInfoToast("Selecciona una herramienta de cobro");
      submitButton.disabled = false;
      return;
    }

    const selectValidations = [
      { selector: "#gestion_cobro", mensaje: "Selecciona una gestión de cobro" },
      { selector: "#estado_llamada", mensaje: "Selecciona un estado de llamada" },
    ];

    for (const { selector, mensaje } of selectValidations) {
      const el = form.querySelector(selector);
      if (!el.value || el.value.includes("Seleccione")) {
        await showInfoToast(mensaje);
        el.focus();
        submitButton.disabled = false;
        return;
      }
    }

    const comentarios = form.querySelector("#comentarios");
    if (!comentarios.value.trim()) {
      await showInfoToast("Escribe un comentario");
      comentarios.focus();
      submitButton.disabled = false;
      return;
    }

    // Si llega aquí, todo está validado
    formSubmitting = true; // evita que vuelva a entrar
    form.submit(); // Enviar el formulario
  });
});

