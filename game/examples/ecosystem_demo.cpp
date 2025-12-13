/**
 * Ecosystem Demo - v0.02 Forest Simulation
 *
 * Loads 'forest-ecosystem.json' and simulates the relational dynamics.
 */

#include "core/RPEngine.h"
#include "core/World.h"
#include "core/Entity.h"
#include "utils/JsonLoader.h"
#include "rules/ForestRules.h"

#include <iostream>
#include <fstream>
#include <sstream>
#include <filesystem>
#include <iomanip>

using namespace RPE;

std::string loadFile(const std::string& path) {
    std::ifstream t(path);
    std::stringstream buffer;
    buffer << t.rdbuf();
    return buffer.str();
}

int main() {
    std::cout << "=== RPE Forest Ecosystem Simulation v0.02 ===" << std::endl;
    
    // 1. Initialize World
    World world;
    RPEngine engine(world);
    engine.setVerbose(false); // Less noise for now

    // 2. Load Data
    std::cout << "Loading forest-ecosystem.json..." << std::endl;
    // Assuming the json is in the parent directory of the build, or we act as if we are in root
    // We will try hardcoded path for the user's environment to be safe or relative
    
    // Check common locations
    std::vector<std::string> paths = {
        "../forest-ecosystem.json",
        "../../forest-ecosystem.json",
        "C:/Users/nscha/Documents/E^2/rpexport/forest-ecosystem.json"
    };
    
    bool loaded = false;
    for (const auto& p : paths) {
        if (std::filesystem::exists(p)) {
            std::string content = loadFile(p);
            if (Utils::JsonLoader::loadForestEcosystem(world, content)) {
                std::cout << "Successfully loaded from: " << p << std::endl;
                loaded = true;
                break;
            }
        }
    }

    if (!loaded) {
        std::cerr << "Failed to find or load forest-ecosystem.json" << std::endl;
        return 1;
    }

    std::cout << "Loaded " << world.getEntities().size() << " entities." << std::endl;

    // 3. Register Forest Rules
    ForestRules::RegisterForestRules(engine);

    // 4. Run Simulation
    std::cout << "\nStarting Simulation (50 ticks)..." << std::endl;
    std::cout << std::string(80, '-') << std::endl;
    std::cout << std::left << std::setw(20) << "Tick" 
              << std::setw(15) << "Oak Pop" << std::setw(15) << "Deer Pop" 
              << std::setw(15) << "Wolf Pop" << std::endl;
    std::cout << std::string(80, '-') << std::endl;

    for (int tick = 1; tick <= 50; ++tick) {
        engine.tick();

        // Log specific entities of interest
        if (tick % 5 == 0) {
            auto* oak = world.getEntity("oak_tree");
            auto* deer = world.getEntity("deer");
            auto* wolf = world.getEntity("wolf");
            
            double oakPop = oak ? oak->getState<double>("population", 0.0) : 0.0;
            double deerPop = deer ? deer->getState<double>("population", 0.0) : 0.0;
            double wolfPop = wolf ? wolf->getState<double>("population", 0.0) : 0.0;

            std::cout << std::left << std::setw(20) << tick 
                      << std::setw(15) << std::fixed << std::setprecision(1) << oakPop
                      << std::setw(15) << deerPop
                      << std::setw(15) << wolfPop << std::endl;
        }
    }

    std::cout << std::string(80, '-') << std::endl;
    std::cout << "Simulation Complete." << std::endl;

    return 0;
}

