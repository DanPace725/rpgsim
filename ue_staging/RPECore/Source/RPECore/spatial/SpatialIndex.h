#pragma once

#include <vector>
#include <string>
#include <unordered_map>

namespace RPE {

struct Vec2 {
    float x, y;

    Vec2() : x(0), y(0) {}
    Vec2(float x, float y) : x(x), y(y) {}

    float distanceTo(const Vec2& other) const;
    float distanceSquaredTo(const Vec2& other) const;
};

struct AABB {
    Vec2 min;
    Vec2 max;

    AABB() = default;
    AABB(const Vec2& min, const Vec2& max) : min(min), max(max) {}

    bool contains(const Vec2& point) const;
    bool intersects(const AABB& other) const;
    float area() const;
};

/**
 * SpatialIndex - Spatial acceleration structure for geometry queries
 *
 * Uses a simple grid-based spatial hash for now. Can be upgraded to
 * quadtree/octree or BVH for better performance later.
 */
class SpatialIndex {
public:
    SpatialIndex(float cellSize = 50.0f);

    // Entity position management
    void updatePosition(const std::string& entityId, const Vec2& position);
    void removeEntity(const std::string& entityId);

    // Spatial queries
    std::vector<std::string> queryRadius(const Vec2& center, float radius) const;
    std::vector<std::string> queryAABB(const AABB& bounds) const;
    std::vector<std::string> queryNearest(const Vec2& point, size_t count) const;

    // Get entity position
    bool getPosition(const std::string& entityId, Vec2& outPosition) const;

private:
    struct GridCell {
        int x, y;

        bool operator==(const GridCell& other) const {
            return x == other.x && y == other.y;
        }
    };

    struct GridCellHash {
        size_t operator()(const GridCell& cell) const {
            return std::hash<int>()(cell.x) ^ (std::hash<int>()(cell.y) << 1);
        }
    };

    float m_cellSize;
    std::unordered_map<std::string, Vec2> m_entityPositions;
    std::unordered_map<GridCell, std::vector<std::string>, GridCellHash> m_grid;

    GridCell positionToCell(const Vec2& pos) const;
    void updateGrid(const std::string& entityId, const Vec2& position);
};

} // namespace RPE
