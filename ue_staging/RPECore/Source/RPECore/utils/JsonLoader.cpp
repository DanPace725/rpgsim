#include "utils/JsonLoader.h"
#include "utils/SimpleJson.h"
#include "core/Entity.h"
#include "core/Relation.h"
#include <iostream>

namespace Utils {

bool JsonLoader::loadForestEcosystem(RPE::World& world, const std::string& jsonContent) {
    try {
        auto root = SimpleJson::parse(jsonContent);
        if (root->type != JsonType::Object) {
            std::cerr << "Error: Root must be an object" << std::endl;
            return false;
        }

        auto& rootObj = root->asObject();

        // 1. Process Nodes (Entities)
        if (rootObj.count("nodes") && rootObj.at("nodes")->type == JsonType::Array) {
            auto& nodes = rootObj.at("nodes")->asArray();
            for (const auto& nodeVal : nodes) {
                auto& node = nodeVal->asObject();
                std::string id = node.at("id")->asString();
                std::string type = node.at("type")->asString();

                // Create Entity
                RPE::Entity* entity = world.createEntity(id, type);
                
                // Set default label
                 if (node.count("label")) {
                    entity->setState("label", node.at("label")->asString());
                 }

                // Parse RP values
                if (node.count("rp") && node.at("rp")->type == JsonType::Object) {
                    auto& rp = node.at("rp")->asObject();
                    for (const auto& [key, val] : rp) {
                        entity->setState(key, val->asDouble());
                    }
                }
                
                // Initialize default state based on type
                entity->setState("exists", true);
                if (type == "producer" || type == "consumer" || type == "predator" || type == "apex") {
                    entity->setState("energy", 50.0);
                    entity->setState("max_energy", 100.0);
                    entity->setState("population", 10.0); // Abstract population count
                } else if (type == "resource" || type == "water") {
                    entity->setState("amount", 100.0);
                    entity->setState("max_amount", 100.0);
                }
            }
        }

        // 2. Process Edges (Relations)
        if (rootObj.count("edges") && rootObj.at("edges")->type == JsonType::Array) {
            auto& edges = rootObj.at("edges")->asArray();
            for (const auto& edgeVal : edges) {
                auto& edge = edgeVal->asObject();
                std::string source = edge.at("source")->asString();
                std::string target = edge.at("target")->asString();
                std::string type = edge.at("type")->asString();
                double weight = edge.at("weight")->asDouble();

                // Map string types to RPE::Primitive enum
                RPE::Primitive primitive = RPE::Primitive::DYNAMICS; // Default
                if (type == "influence") primitive = RPE::Primitive::DYNAMICS;
                else if (type == "constraint") primitive = RPE::Primitive::CONSTRAINT;
                else if (type == "info") primitive = RPE::Primitive::EPISTEMIC;
                else if (type == "meta") primitive = RPE::Primitive::META;
                else if (type == "geometry") primitive = RPE::Primitive::GEOMETRY;

                RPE::Relation relation(primitive, source, target, type);
                relation.setPayload(weight);
                world.addRelation(relation);
            }
        }

        return true;
    } catch (const std::exception& e) {
        std::cerr << "JSON Load Error: " << e.what() << std::endl;
        return false;
    }
}

} // namespace Utils
