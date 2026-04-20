#undef TABLE_ITEM

/* clang-format off */
#if defined(_SCAN_TEMPLATE_ARRAY)
   #define TABLE_ITEM(_w, _a) { .w = (_w), .a = (_a)},
#else
   #define TABLE_ITEM(_w, _a)
#endif
/* clang-format on */

#undef _SCAN_TEMPLATE_ARRAY
