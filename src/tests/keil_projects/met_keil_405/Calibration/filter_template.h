#undef TABLE_ITEM

/* clang-format off */
#if defined(_FILTER_TEMPLATE_ARRAY)
   #define TABLE_ITEM(_f, _fn) { .centerFreq = (_f), .filterFactory = (_fn)},
#else
   #define TABLE_ITEM(_f, _fn)
#endif
/* clang-format on */

#undef _FILTER_TEMPLATE_ARRAY
