#include "spatial/SpatialIndex.h"
#include <cmath>
#include <algorithm>
#include <limits>

namespace RPE {

float Vec2::distanceTo(const Vec2& other) const {
    float dx = x - other.x;
    float dy = y - other.y;
    return std::sqrt(dx * dx + dy * dy);
}

float Vec2::distanceSquaredTo(const Vec2& other) const {
    float dx = x - other.x;
    float dy = y - other.y;
    return dx * dx + dy * dy;
}

bool AABB::contains(const Vec2& point) const {
    return point.x >= min.x && point.x <= max.x &&
           point.y >= min.y && point.y <= max.y;
}

bool AABB::intersects(const AABB& other) const {
    return !(other.min.x > max.x || other.max.x < min.x ||
             other.min.y > max.y || other.max.y < min.y);
}

float AABB::area() const {
    return (max.x - min.x) * (max.y - min.y);
}

SpatialIndex::SpatialIndex(float cellSize)
    : m_cellSize(cellSize)
{
}

void SpatialIndex::updatePosition(const std::string& entityId, const Vec2& position) {
    // Remove from old cell if exists
    auto it = m_entityPositions.find(entityId);
    if (it != m_entityPositions.end()) {
        GridCell oldCell = positionToCell(it->second);
        auto& cellEntities = m_grid[oldCell];
        cellEntities.erase(std::remove(cellEntities.begin(), cellEntities.end(), entityId),
                          cellEntities.end());
    }

    // Update position and add to new cell
    m_entityPositions[entityId] = position;
    updateGrid(entityId, position);
}

void SpatialIndex::removeEntity(const std::string& entityId) {
    auto it = m_entityPositions.find(entityId);
    if (it != m_entityPositions.end()) {
        GridCell cell = positionToCell(it->second);
        auto& cellEntities = m_grid[cell];
        cellEntities.erase(std::remove(cellEntities.begin(), cellEntities.end(), entityId),
                          cellEntities.end());
        m_entityPositions.erase(it);
    }
}

std::vector<std::string> SpatialIndex::queryRadius(const Vec2& center, float radius) const {
    std::vector<std::string> result;
    float radiusSquared = radius * radius;

    // Calculate cell range to check
    int cellRadius = static_cast<int>(std::ceil(radius / m_cellSize));
    GridCell centerCell = positionToCell(center);

    for (int dy = -cellRadius; dy <= cellRadius; ++dy) {
        for (int dx = -cellRadius; dx <= cellRadius; ++dx) {
            GridCell cell{centerCell.x + dx, centerCell.y + dy};
            auto it = m_grid.find(cell);
            if (it != m_grid.end()) {
                for (const auto& entityId : it->second) {
                    auto posIt = m_entityPositions.find(entityId);
                    if (posIt != m_entityPositions.end()) {
                        if (posIt->second.distanceSquaredTo(center) <= radiusSquared) {
                            result.push_back(entityId);
                        }
                    }
                }
            }
        }
    }

    return result;
}

std::vector<std::string> SpatialIndex::queryAABB(const AABB& bounds) const {
    std::vector<std::string> result;

    GridCell minCell = positionToCell(bounds.min);
    GridCell maxCell = positionToCell(bounds.max);

    for (int y = minCell.y; y <= maxCell.y; ++y) {
        for (int x = minCell.x; x <= maxCell.x; ++x) {
            GridCell cell{x, y};
            auto it = m_grid.find(cell);
            if (it != m_grid.end()) {
                for (const auto& entityId : it->second) {
                    auto posIt = m_entityPositions.find(entityId);
                    if (posIt != m_entityPositions.end()) {
                        if (bounds.contains(posIt->second)) {
                            result.push_back(entityId);
                        }
                    }
                }
            }
        }
    }

    return result;
}

std::vector<std::string> SpatialIndex::queryNearest(const Vec2& point, size_t count) const {
    std::vector<std::pair<float, std::string>> candidates;

    // Collect all entities with distances
    for (const auto& [entityId, pos] : m_entityPositions) {
        float distSq = point.distanceSquaredTo(pos);
        candidates.emplace_back(distSq, entityId);
    }

    // Partial sort to get k nearest
    size_t k = std::min(count, candidates.size());
    std::partial_sort(candidates.begin(),
                     candidates.begin() + k,
                     candidates.end(),
                     [](const auto& a, const auto& b) {
                         return a.first < b.first;
                     });

    std::vector<std::string> result;
    result.reserve(k);
    for (size_t i = 0; i < k; ++i) {
        result.push_back(candidates[i].second);
    }

    return result;
}

bool SpatialIndex::getPosition(const std::string& entityId, Vec2& outPosition) const {
    auto it = m_entityPositions.find(entityId);
    if (it != m_entityPositions.end()) {
        outPosition = it->second;
        return true;
    }
    return false;
}

SpatialIndex::GridCell SpatialIndex::positionToCell(const Vec2& pos) const {
    return GridCell{
        static_cast<int>(std::floor(pos.x / m_cellSize)),
        static_cast<int>(std::floor(pos.y / m_cellSize))
    };
}

void SpatialIndex::updateGrid(const std::string& entityId, const Vec2& position) {
    GridCell cell = positionToCell(position);
    m_grid[cell].push_back(entityId);
}

} // namespace RPE
