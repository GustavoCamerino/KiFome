document.addEventListener('click', (e)=>{
  const add = e.target.closest('.add-to-cart');
  if(add){
    const pratoId = add.dataset.id;
    fetch('/carrinho/add', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({prato_id:pratoId, quantidade:1})})
      .then(r=>r.json()).then(data=>{
        if(data.error){ alert(data.error); }
        else{ alert('Adicionado ao carrinho!'); }
      });
  }
  const q = e.target.closest('.qtde');
  if(q){
    const id = q.dataset.id; const delta = parseInt(q.dataset.delta,10);
    const qtdSpan = document.getElementById('qtd-'+id);
    const nova = Math.max(0, parseInt(qtdSpan.textContent||'1',10)+delta);
    fetch('/carrinho/update', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({prato_id:id, quantidade:nova})})
      .then(r=>r.json()).then(data=>{
        if(data.error){ alert(data.error); }
        else{ qtdSpan.textContent = nova; document.getElementById('subtotal').textContent = data.subtotal.toFixed(2); document.getElementById('taxa').textContent = data.taxa.toFixed(2); document.getElementById('total').textContent = data.total.toFixed(2); if(nova===0){ location.reload(); } }
      });
  }
  const rem = e.target.closest('.remove');
  if(rem){
    const id = rem.dataset.id;
    fetch('/carrinho/remove', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({prato_id:id})})
      .then(r=>r.json()).then(()=>location.reload());
  }
});

