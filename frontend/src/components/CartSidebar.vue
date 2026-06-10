<template>
  <van-action-sheet v-model:show="visible" title="购物车" :close-on-click-action="false">
    <div class="cart-sidebar-list">
      <div v-for="item in items" :key="item.id" class="cart-item">
        <span class="ci-name">{{ item.name }}</span>
        <div class="ci-ctrl">
          <button class="ci-btn" @click="$emit('remove', item)">−</button>
          <span class="ci-qty">{{ item.qty }}</span>
          <button class="ci-btn ci-plus" @click="$emit('add', item)">+</button>
        </div>
        <span class="ci-price">¥{{ (item.price * item.qty).toFixed(1) }}</span>
      </div>
    </div>
    <div class="cart-footer">
      <van-button type="primary" block round @click="$emit('clear')">清空购物车</van-button>
    </div>
  </van-action-sheet>
</template>

<script setup>
import { ref, watch } from 'vue'
const props = defineProps({ show: Boolean, items: { type: Array, default: () => [] } })
const emit = defineEmits(['update:show', 'add', 'remove', 'clear'])
const visible = ref(false)
watch(() => props.show, (val) => { visible.value = val })
watch(visible, (val) => { emit('update:show', val) })
</script>

<style scoped>
.cart-sidebar-list { max-height: 300px; overflow-y: auto; padding: 0 18px; }
.cart-item { display: flex; align-items: center; padding: 12px 0; border-bottom: 1px solid var(--clay-divider); font-size: 14px; }
.ci-name { flex: 1; color: var(--clay-text); }
.ci-ctrl { display: flex; align-items: center; gap: 10px; margin: 0 14px; }
.ci-btn {
  width: 26px; height: 26px; border-radius: 50%;
  border: 1.5px solid var(--clay-brand); background: transparent;
  color: var(--clay-brand); font-size: 14px; font-weight: 600;
  cursor: pointer; display: flex; align-items: center; justify-content: center;
  transition: all 0.2s var(--spring); font-family: inherit; line-height: 1;
}
.ci-plus { background: var(--clay-brand); color: #fff; }
.ci-btn:active { transform: scale(0.9); }
.ci-qty { font-size: 15px; font-weight: 700; color: var(--clay-text); min-width: 20px; text-align: center; }
.ci-price { color: var(--clay-brand); font-weight: 600; }
.cart-footer { padding: 16px 18px; }
</style>
