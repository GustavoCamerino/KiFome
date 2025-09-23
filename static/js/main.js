// Mobile nav toggle
(function(){
  const toggle = document.querySelector('.nav-toggle');
  const links = document.getElementById('nav-links');
  if (toggle && links) {
    toggle.addEventListener('click', () => {
      const open = links.classList.toggle('open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }
})();

// Auto-hide messages
setTimeout(()=>{
  document.querySelectorAll('.messages li').forEach(el=> el.style.display='none');
}, 4000);

// Home search filter
(function(){
  const input = document.getElementById('filterRestaurants');
  const grid = document.getElementById('restaurantsGrid');
  const empty = document.getElementById('noResults');
  if (!input || !grid) return;
  const apply = () => {
    const q = (input.value || '').toLowerCase().trim();
    let visible = 0;
    grid.querySelectorAll('.card').forEach(card => {
      const name = card.getAttribute('data-name') || '';
      const cuisine = card.getAttribute('data-cuisine') || '';
      const show = !q || name.includes(q) || cuisine.includes(q);
      card.style.display = show ? 'block' : 'none';
      if (show) visible++;
    });
    if (empty) empty.style.display = visible ? 'none' : 'block';
  };
  input.addEventListener('input', apply);
  // Apply on load if there is a preset value (from server-side query)
  if ((input.value || '').trim().length > 0) {
    apply();
  }
})();

// Auto-refresh order tracking when status changes
(function(){
  const root = document.getElementById('tracking-root');
  if (!root) return;
  const pedidoId = root.getAttribute('data-pedido-id');
  let current = root.getAttribute('data-status');
  const poll = () => {
    fetch(`/pedidos/pedido/${pedidoId}/status/`, {headers:{'Accept':'application/json'}})
      .then(r=> r.ok ? r.json() : null)
      .then(data => {
        if (!data) return;
        if (data.status && data.status !== current) {
          current = data.status;
          // Atualiza texto de status
          const panel = document.querySelector('.panel');
          const statusP = panel ? panel.querySelector('p strong') : null;
          if (statusP) statusP.textContent = data.status_display;
          // Atualiza steps
          const steps = document.querySelectorAll('.steps .step');
          steps.forEach(s => s.classList.remove('active'));
          if (current !== 'pendente') steps[0]?.classList.add('active');
          if (current === 'transito' || current === 'entregue') steps[1]?.classList.add('active');
          if (current === 'entregue') steps[2]?.classList.add('active');
          // Atualiza rótulo do botão, se existir
          const form = document.querySelector('form[action*="/pedidos/pedido/"][action$="/avancar/"]');
          const btn = form ? form.querySelector('button') : null;
          if (btn) {
            if (current === 'pendente') btn.textContent = 'Em preparo';
            else if (current === 'preparacao') btn.textContent = 'Finalizado (enviar)';
            else if (current === 'transito') btn.textContent = 'Concluir pedido';
            else form.remove();
          }
        }
      })
      .catch(()=>{});
  };
  setInterval(poll, 4000);
})();
// Add to cart via AJAX and badge update
(function(){
  const links = document.querySelectorAll('.js-add-to-cart');
  const buyNowLinks = document.querySelectorAll('.js-buy-now');
  if (!links.length && !buyNowLinks.length) return;
  const badge = document.getElementById('cart-count');
  const toast = (msg) => {
    const ul = document.querySelector('.messages') || (()=>{const u=document.createElement('ul');u.className='messages';document.querySelector('.container')?.prepend(u);return u})();
    const li = document.createElement('li'); li.className='success'; li.textContent=msg; ul.appendChild(li); setTimeout(()=>li.remove(),3000);
  };
  const updateBadge = () => {
    fetch('/pedidos/carrinho/summary/', {headers:{'Accept':'application/json'}})
      .then(r=>r.ok?r.json():null)
      .then(data=>{ if (data && badge) badge.textContent = data.count; })
      .catch(()=>{});
  };
  updateBadge();
  const getQtyFor = (el) => {
    // procura input.qty-input anterior no mesmo card
    const card = el.closest('.card');
    const input = card ? card.querySelector('input.qty-input') : null;
    const v = input ? parseInt(input.value || '1', 10) : 1;
    return isNaN(v) || v < 1 ? 1 : v;
  };
  links.forEach(a => {
    a.addEventListener('click', (e)=>{
      e.preventDefault();
      const qty = getQtyFor(a);
      const url = a.href + `?qty=${encodeURIComponent(qty)}`;
      fetch(url, {headers:{'X-Requested-With':'XMLHttpRequest','Accept':'application/json'}})
        .then(r=>r.ok?r.json():null)
        .then(data=>{
          if (data && data.ok){ if (badge) badge.textContent = data.count; toast('Adicionado ao carrinho!'); }
          else if (data && data.error){ toast(data.error); }
        })
        .catch(()=>{});
    });
  });
  buyNowLinks.forEach(a => {
    a.addEventListener('click', (e)=>{
      e.preventDefault();
      const qty = getQtyFor(a);
      // para buy now, só suportamos qty=1 por simplicidade no backend; se >1, adiciona ao carrinho e redireciona para checkout
      if (qty !== 1) {
        const addUrl = a.href.replace('/comprar/','/carrinho/add/') + `?qty=${qty}`;
        fetch(addUrl, {headers:{'X-Requested-With':'XMLHttpRequest','Accept':'application/json'}})
          .then(()=>{ window.location.href = '/pedidos/checkout/'; });
      } else {
        window.location.href = a.href; // fluxo existente faz buy_now e segue para checkout
      }
    });
  });
})();

// Restaurante dashboard live update
(function(){
  const root = document.getElementById('dashboard-root');
  const list = document.getElementById('pedidos-list');
  const lucroSpan = document.getElementById('lucro-valor');
  if (!root || !list || !lucroSpan) return;
  const render = (data) => {
    // Recalcula lucro localmente: soma 97% dos pedidos não cancelados
    if (Array.isArray(data.pedidos)) {
      const lucroCalc = data.pedidos
        .filter(p => p.status !== 'cancelado')
        .reduce((acc, p) => acc + (parseFloat(p.valor_total||'0') * 0.97), 0);
      lucroSpan.textContent = lucroCalc.toFixed(2);
    } else if (data.lucro) {
      lucroSpan.textContent = parseFloat(data.lucro).toFixed(2);
    }
    if (!Array.isArray(data.pedidos)) return;
    const html = data.pedidos.map(p => {
      const clienteFoto = p.cliente_foto ? `<img class="cliente-foto" src="${p.cliente_foto}" alt="${p.cliente_nome}" style="width:40px;height:40px;object-fit:cover;border-radius:999px" />` : '';
      const itens = p.itens.map(it => `${it.quantidade}x ${it.prato_nome}`).join('<br/>');
      let acao = '';
      if (p.status === 'pendente') acao = `<a class="btn avancar" href="/pedidos/pedido/${p.id}/avancar/">Em preparo</a>`;
      else if (p.status === 'preparacao') acao = `<a class="btn avancar" href="/pedidos/pedido/${p.id}/avancar/">Finalizado (enviar)</a>`;
      else if (p.status === 'transito') acao = `<a class="btn avancar" href="/pedidos/pedido/${p.id}/avancar/">Concluir pedido</a>`;
      else acao = `<span class="badge">${p.status_display}</span>`;
      return `
      <div class="pedido" data-id="${p.id}" style="padding:10px 0;border-bottom:1px solid #102544">
        <div style="display:flex;justify-content:space-between;gap:12px;align-items:center;flex-wrap:wrap;">
          <div style="display:flex;gap:10px;align-items:center;">
            ${clienteFoto}
            <div>
              <div><strong class="pid">#${p.id}</strong> — <span class="cliente-nome">${p.cliente_nome}</span> — <span class="status">${p.status_display}</span></div>
              <small class="endereco">${p.endereco_entrega || 'Sem endereço informado'}</small>
            </div>
          </div>
          <div><strong>R$ <span class="valor">${parseFloat(p.valor_total).toFixed(2)}</span></strong></div>
        </div>
        <div class="mt-1 itens">${itens}</div>
        <div class="mt-1 acao">${acao}</div>
      </div>`;
    }).join('');
    list.innerHTML = html || '<div class="empty">Sem pedidos ainda.</div>';
  };
  const poll = () => {
    fetch('/restaurantes/dashboard/data/', {headers:{'Accept':'application/json'}})
      .then(r=>r.ok?r.json():null)
      .then(data=>{ if (data) render(data); })
      .catch(()=>{});
  };
  poll();
  setInterval(poll, 6000);
})();
