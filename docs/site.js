const buttons=[...document.querySelectorAll('[data-filter]')];
const projects=[...document.querySelectorAll('[data-category]')];
function filterProjects(filter){let count=0;for(const card of projects){card.hidden=filter!=='all'&&!card.dataset.category.split(' ').includes(filter);if(!card.hidden)count++;}for(const button of buttons)button.setAttribute('aria-pressed',String(button.dataset.filter===filter));document.querySelector('#filter-note').textContent=`${count} case studies · Original data, analysis and evidence remain in the linked project pages.`;}
buttons.forEach(button=>button.addEventListener('click',()=>filterProjects(button.dataset.filter)));
document.querySelectorAll('a[href^="#"]').forEach(a=>a.addEventListener('click',()=>{const target=document.querySelector(a.getAttribute('href'));if(target?.classList.contains('project'))filterProjects('all');}));
