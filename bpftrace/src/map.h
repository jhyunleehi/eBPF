#pragma once

#include "imap.h"

namespace bpftrace {

class Map : public IMap {
public:
  Map(const std::string &name,
      const SizedType &type,
      const MapKey &key,
      int max_entries)
      : Map(name, type, key, 0, 0, 0, max_entries){};
  Map(const std::string &name,
      const SizedType &type,
      const MapKey &key,
      int min,
      int max,
      int step,
      int max_entries);
  Map(const std::string &name,
      libbpf::bpf_map_type type,
      int key_size,
      int value_size,
      int max_entries,
      int flags);
  Map(const SizedType &type);
  Map(libbpf::bpf_map_type map_type);
  Map(libbpf::bpf_map_type map_type, uint64_t perf_rb_pages);
  virtual ~Map() override;
};
} // namespace bpftrace
