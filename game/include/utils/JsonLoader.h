#pragma once

#include "core/World.h"
#include <string>

namespace Utils {

class JsonLoader {
public:
    static bool loadForestEcosystem(RPE::World& world, const std::string& jsonContent);
};

} // namespace Utils
