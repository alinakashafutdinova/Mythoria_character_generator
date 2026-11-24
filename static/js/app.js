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

// MYTHORIA DECORATIVE SPARKS — небольшая подсветка на первом экране
if (!window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
  const host=document.querySelector('.hero-art');
  if(host) {
    host.style.isolation='isolate';
    for(let i=0;i<10;i++) {
      const spark=document.createElement('span');
      spark.className='my-decor-spark';
      spark.style.cssText='position:absolute;pointer-events:none;z-index:4;width:3px;height:3px;border-radius:50%;background:'+(i%2?'#ff82d8':'#55eafd')+';box-shadow:0 0 15px currentColor;left:'+((17*i+9)%93)+'%;top:'+((29*i+7)%88)+'%;animation:mySpark '+(5+i%4)+'s ease-in-out infinite '+(-i%4)+'s';
      host.append(spark);
    }
  }
}
