'use strict';
const menu = document.querySelector('.mobile-nav-toggle');
const nav = document.querySelector('.main-nav');
if (menu && nav) menu.addEventListener('click', () => {
  const expanded = menu.getAttribute('aria-expanded') === 'true';
  menu.setAttribute('aria-expanded', String(!expanded));
  nav.classList.toggle('open', !expanded);
});
for (const form of document.querySelectorAll('form[data-confirm]')) {
  form.addEventListener('submit', event => {
    if (!window.confirm(form.dataset.confirm)) event.preventDefault();
  });
}
const filterTabs = document.querySelectorAll('.tab[data-filter]');
const gameCards = document.querySelectorAll('.game-card[data-group]');
for (const tab of filterTabs) {
  tab.addEventListener('click', () => {
    for (const t of filterTabs) t.classList.toggle('active', t === tab);
    for (const card of gameCards) card.hidden = tab.dataset.filter !== 'all' && card.dataset.group !== tab.dataset.filter;
  });
}

// Карусель миров: работает с клавиатуры и кнопками.
for (const carousel of document.querySelectorAll('[data-carousel]')) {
  const track = carousel.querySelector('[data-carousel-track]');
  for (const [direction, selector] of [[-1,'[data-carousel-prev]'],[1,'[data-carousel-next]']]) {
    carousel.querySelector(selector)?.addEventListener('click', () => {
      const step = track.querySelector('.spotlight-card')?.getBoundingClientRect().width || 300;
      track.scrollBy({left:direction*(step+17),behavior:'smooth'});
    });
  }
}
