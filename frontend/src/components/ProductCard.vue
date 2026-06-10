<template>
  <div class="product-card-comp">
    <div class="pc-img">
      <img :src="product.image || 'https://img.yzcdn.cn/vant/cat.jpeg'" :alt="product.name" />
    </div>
    <div class="pc-body">
      <div class="pc-name">{{ product.name }}</div>
      <div class="pc-desc" v-if="product.description">{{ product.description }}</div>
      <div class="pc-meta">
        <span class="pc-sales">月售{{ product.sales || 0 }}</span>
      </div>
      <div class="pc-row">
        <span class="pc-price">¥<b>{{ product.price }}</b></span>
        <div class="pc-ctrl">
          <button v-if="quantity > 0" class="pc-btn" @click="$emit('remove', product)">−</button>
          <span v-if="quantity > 0" class="pc-qty">{{ quantity }}</span>
          <button class="pc-btn pc-plus" @click="$emit('add', product)">+</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  product: { type: Object, required: true },
  quantity: { type: Number, default: 0 }
})
defineEmits(['add', 'remove'])
</script>

<style scoped>
.product-card-comp {
  display: flex; gap: 14px;
  background: var(--clay-card);
  border-radius: 16px; padding: 14px;
  margin-bottom: 10px;
  border: 1px solid var(--clay-border);
  transition: all 0.2s var(--spring);
}
.product-card-comp:active { background: var(--clay-card-warm); transform: scale(0.985); }
.pc-img { width: 80px; height: 80px; border-radius: 12px; overflow: hidden; flex-shrink: 0; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
.pc-img img { width: 100%; height: 100%; object-fit: cover; }
.pc-body { flex: 1; display: flex; flex-direction: column; justify-content: space-between; min-width: 0; }
.pc-name { font-size: 15px; font-weight: 600; color: var(--clay-text); }
.pc-desc { font-size: 12px; color: var(--clay-text-soft); }
.pc-sales { font-size: 11px; color: var(--clay-text-muted); }
.pc-row { display: flex; justify-content: space-between; align-items: center; margin-top: 4px; }
.pc-price { font-family: Georgia, serif; color: var(--clay-brand); font-size: 12px; }
.pc-price b { font-size: 20px; font-weight: 700; }
.pc-ctrl { display: flex; align-items: center; gap: 8px; }
.pc-btn {
  width: 28px; height: 28px; border-radius: 50%;
  border: 1.5px solid var(--clay-brand); background: transparent;
  color: var(--clay-brand); font-size: 16px; font-weight: 600;
  cursor: pointer; display: flex; align-items: center; justify-content: center;
  transition: all 0.2s var(--spring); font-family: inherit; line-height: 1;
}
.pc-btn:active { transform: scale(0.9); }
.pc-plus { background: var(--clay-brand); color: #fff; }
.pc-qty { font-size: 15px; font-weight: 700; color: var(--clay-text); min-width: 20px; text-align: center; }
</style>
