(() => {
  const body = document.body;
  const toggle = document.querySelector(".menu-toggle");
  const sidebar = document.querySelector(".sidebar");

  if (!toggle || !sidebar) {
    return;
  }

  const closeSidebar = () => {
    body.classList.remove("sidebar-open");
  };

  toggle.addEventListener("click", () => {
    body.classList.toggle("sidebar-open");
  });

  sidebar.addEventListener("click", (event) => {
    const target = event.target;
    if (target instanceof HTMLElement && target.closest("a")) {
      closeSidebar();
    }
  });

  window.addEventListener("resize", () => {
    if (window.innerWidth > 900) {
      closeSidebar();
    }
  });

  const foodPicker = document.querySelector(".food-picker");
  if (!foodPicker) {
    return;
  }

  const modal = document.getElementById("food-modal");
  const openButtons = document.querySelectorAll("[data-open-food-modal]");
  const closeButtons = document.querySelectorAll("[data-close-food-modal]");
  const foodGrid = document.getElementById("food-grid");
  const foodEmpty = document.getElementById("food-empty");
  const foodSearch = document.getElementById("food-search");
  const selectedLabel = document.getElementById("food-selected");
  const foodSelect = document.querySelector("select[name='food']");
  const amountField = document.querySelector("input[name='amount_g']");
  const foodsUrl = foodPicker.dataset.foodsUrl;
  const placeholderUrl = foodPicker.dataset.placeholderUrl;
  let selectedFood = null;

  const toggleModal = (isOpen) => {
    if (!modal) {
      return;
    }
    modal.classList.toggle("is-open", isOpen);
    modal.setAttribute("aria-hidden", (!isOpen).toString());
    if (isOpen && foodSearch) {
      foodSearch.focus();
    }
  };

  const setSelectedFood = (food) => {
    if (!foodSelect || !selectedLabel) {
      return;
    }
    selectedFood = food;
    let option = foodSelect.querySelector(`option[value="${food.id}"]`);
    if (!option) {
      option = new Option(food.name, food.id);
      foodSelect.add(option);
    }
    foodSelect.value = String(food.id);
    selectedLabel.textContent = `${food.name} · ${Math.round(food.calories_per_100g)} kcal/100g`;
    if (amountField) {
      amountField.required = true;
    }
  };

  const renderFoods = (foods) => {
    if (!foodGrid) {
      return;
    }
    foodGrid.innerHTML = "";
    if (!foods.length) {
      if (foodEmpty) {
        foodEmpty.hidden = false;
      }
      return;
    }
    if (foodEmpty) {
      foodEmpty.hidden = true;
    }
    foods.forEach((food) => {
      const card = document.createElement("div");
      card.className = "food-card";

      const image = document.createElement("img");
      image.alt = food.name;
      image.src = food.image_url || placeholderUrl;
      image.onerror = () => {
        image.src = placeholderUrl;
      };

      const title = document.createElement("div");
      title.className = "food-card-title";
      title.textContent = food.name;

      const meta = document.createElement("div");
      meta.className = "food-card-meta";
      meta.textContent = `${Math.round(food.calories_per_100g)} kcal / 100g`;

      const actions = document.createElement("div");
      actions.className = "food-card-actions";

      const addBtn = document.createElement("button");
      addBtn.type = "button";
      addBtn.className = "button small";
      addBtn.textContent = "Añadir";
      addBtn.addEventListener("click", () => {
        setSelectedFood(food);
        toggleModal(false);
      });

      const infoBtn = document.createElement("button");
      infoBtn.type = "button";
      infoBtn.className = "button ghost small";
      infoBtn.textContent = "Información";

      const info = document.createElement("div");
      info.className = "food-card-info";
      info.innerHTML = `
        <span>Proteinas: ${food.protein_per_100g} g</span>
        <span>Carbohidratos: ${food.carbs_per_100g} g</span>
        <span>Grasas: ${food.fat_per_100g} g</span>
        <span>Calorias: ${food.calories_per_100g} kcal</span>
      `;

      infoBtn.addEventListener("click", () => {
        info.classList.toggle("is-open");
      });

      actions.append(addBtn, infoBtn);
      card.append(image, title, meta, actions, info);
      foodGrid.append(card);
    });
  };

  const fetchFoods = async (query = "") => {
    if (!foodsUrl) {
      return;
    }
    const url = new URL(foodsUrl, window.location.origin);
    url.searchParams.set("limit", "50");
    if (query) {
      url.searchParams.set("q", query);
    }
    const response = await fetch(url.toString());
    if (!response.ok) {
      renderFoods([]);
      return;
    }
    const data = await response.json();
    renderFoods(Array.isArray(data) ? data : []);
  };

  const debounce = (fn, wait = 250) => {
    let timeoutId;
    return (...args) => {
      clearTimeout(timeoutId);
      timeoutId = window.setTimeout(() => fn(...args), wait);
    };
  };

  openButtons.forEach((button) => {
    button.addEventListener("click", () => {
      toggleModal(true);
      fetchFoods("");
    });
  });

  closeButtons.forEach((button) => {
    button.addEventListener("click", () => toggleModal(false));
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      toggleModal(false);
    }
  });

  if (foodSearch) {
    const handleSearch = debounce((event) => {
      fetchFoods(event.target.value.trim());
    }, 300);
    foodSearch.addEventListener("input", handleSearch);
  }

})();

