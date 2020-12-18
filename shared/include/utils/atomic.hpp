#pragma once

#include <atomic>

namespace utils {

/// @brief Atomically performs the operation of `updater` on `atomic`
/// @details `updater` may be called multiple times per one call of
/// `AtomicUpdate`, so it must be idempotent. To ensure that the function does
/// not spin for a long time, `updater` must be fairly simple and fast.
/// @param atomic the variable to update
/// @param updater a lambda that takes the old value and produces the new value
/// @return The updated value
template <typename T, typename Func>
T AtomicUpdate(std::atomic<T>& atomic, Func updater) {
  T old_value = atomic.load();
  while (true) {
    const T new_value = updater(T(old_value));
    if (atomic.compare_exchange_weak(old_value, new_value)) return new_value;
  }
}

/// Makes sure `atomic <= value`
template <typename T>
T AtomicMin(std::atomic<T>& atomic, T value) {
  return utils::AtomicUpdate(atomic, [value](T old_value) {
    return value < old_value ? value : old_value;
  });
}

/// Makes sure `atomic >= value`
template <typename T>
T AtomicMax(std::atomic<T>& atomic, T value) {
  return utils::AtomicUpdate(atomic, [value](T old_value) {
    return old_value < value ? value : old_value;
  });
}

}  // namespace utils