(() => {
  const stage = document.querySelector("[data-body-stage]");
  const model = document.querySelector("[data-body-model]");
  if (!stage || !model) return;

  const layerButtons = [...document.querySelectorAll("[data-body-layer]:not(.body-layer)")];
  const svgLayers = [...model.querySelectorAll(".body-layer")];
  const partLists = [...document.querySelectorAll(".body-part-list")];
  const svgParts = [...model.querySelectorAll(".anatomy-hit")];
  const name = document.querySelector("[data-detail-name]");
  const system = document.querySelector("[data-detail-system]");
  const description = document.querySelector("[data-detail-function]");
  const fact = document.querySelector("[data-detail-fact]");
  let zoom = 1;
  let rotateX = -2;
  let rotateY = -12;
  let pointerStart = null;
  let dragged = false;

  const setTransform = () => {
    model.style.transform = `rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale(${zoom})`;
  };

  const selectPart = (id) => {
    const button = partLists
      .filter((list) => !list.hidden)
      .flatMap((list) => [...list.querySelectorAll(".body-part-button")])
      .find((item) => item.dataset.anatomyId === id);
    if (!button) return;
    for (const item of document.querySelectorAll(".body-part-button")) {
      const selected = item === button;
      item.classList.toggle("selected", selected);
      item.setAttribute("aria-pressed", String(selected));
    }
    for (const item of svgParts) {
      item.classList.toggle("is-selected", item.dataset.anatomyId === id);
    }
    name.textContent = button.dataset.name;
    system.textContent = button.dataset.system;
    description.textContent = button.dataset.function;
    fact.textContent = button.dataset.fact;
  };

  const changeLayer = (id) => {
    for (const button of layerButtons) {
      const active = button.dataset.bodyLayer === id;
      button.classList.toggle("active", active);
      button.setAttribute("aria-pressed", String(active));
    }
    for (const layer of svgLayers) {
      const active = layer.dataset.bodyLayer === id;
      if (active) layer.removeAttribute("hidden");
      else layer.setAttribute("hidden", "");
      layer.setAttribute("aria-hidden", String(!active));
    }
    for (const list of partLists) {
      list.hidden = list.dataset.partList !== id;
    }
    const activeList = partLists.find((list) => list.dataset.partList === id);
    const activePart = activeList?.querySelector('.body-part-button[aria-pressed="true"]')
      || activeList?.querySelector(".body-part-button");
    if (activePart) selectPart(activePart.dataset.anatomyId);
  };

  for (const button of layerButtons) {
    button.addEventListener("click", () => changeLayer(button.dataset.bodyLayer));
  }
  for (const button of document.querySelectorAll(".body-part-button")) {
    button.addEventListener("click", () => selectPart(button.dataset.anatomyId));
  }
  for (const part of svgParts) {
    part.addEventListener("click", () => selectPart(part.dataset.anatomyId));
    part.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        selectPart(part.dataset.anatomyId);
      }
    });
  }
  for (const button of document.querySelectorAll("[data-zoom]")) {
    button.addEventListener("click", () => {
      if (button.dataset.zoom === "in") zoom = Math.min(1.45, zoom + 0.12);
      if (button.dataset.zoom === "out") zoom = Math.max(0.82, zoom - 0.12);
      if (button.dataset.zoom === "reset") {
        zoom = 1;
        rotateX = -2;
        rotateY = -12;
      }
      setTransform();
    });
  }

  stage.addEventListener("pointerdown", (event) => {
    pointerStart = { x: event.clientX, y: event.clientY, rotateX, rotateY };
    dragged = false;
    stage.setPointerCapture(event.pointerId);
  });
  stage.addEventListener("pointermove", (event) => {
    if (!pointerStart) return;
    const dx = event.clientX - pointerStart.x;
    const dy = event.clientY - pointerStart.y;
    if (Math.abs(dx) + Math.abs(dy) > 5) dragged = true;
    if (!dragged) return;
    rotateY = Math.max(-40, Math.min(40, pointerStart.rotateY + dx * 0.35));
    rotateX = Math.max(-10, Math.min(10, pointerStart.rotateX - dy * 0.15));
    setTransform();
  });
  const finishDrag = () => {
    if (dragged) window.setTimeout(() => { dragged = false; }, 0);
    pointerStart = null;
  };
  stage.addEventListener("pointerup", finishDrag);
  stage.addEventListener("pointercancel", finishDrag);
  stage.addEventListener("click", (event) => {
    if (dragged) {
      event.preventDefault();
      event.stopPropagation();
    }
  }, true);

  const initialLayer = layerButtons.find((button) => button.getAttribute("aria-pressed") === "true");
  if (initialLayer) changeLayer(initialLayer.dataset.bodyLayer);
  setTransform();
})();
