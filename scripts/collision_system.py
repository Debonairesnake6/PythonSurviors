# scripts/collision_system.py - Complete high-performance collision system
# Generated in part with Claude

from typing import Dict, List, Set, Tuple
from scripts.readable_classes import XYFloat, XYInt
from scripts.config import DISPLAY_SIZE
from entities.enemy import Enemy
from weapons.base_weapon import BaseAmmo
from pygame import FRect


class SpatialGrid:
    def __init__(self, cell_size: int = 64) -> None:  # Smaller cells for better distribution
        self.cell_size: int = cell_size
        # Use tuples for dictionary keys - maximum performance
        self.cells: Dict[tuple[int, int], List[Enemy]] = {}
        self.grid_width: int = (DISPLAY_SIZE.x // cell_size) + 2  # Extra padding
        self.grid_height: int = (DISPLAY_SIZE.y // cell_size) + 2

        # Pre-calculate division for faster cell coordinate calculation
        self.inv_cell_size: float = 1.0 / cell_size

    def get_cell_coords(self, location: XYFloat) -> tuple[int, int]:
        """Convert XYFloat (readable) to tuple (fast) for grid coordinates"""
        # Use multiplication instead of division (faster)
        cell_x: int = int(location.x * self.inv_cell_size)
        cell_y: int = int(location.y * self.inv_cell_size)

        # Return tuple for maximum dict key performance
        clamped_x: int = max(0, min(cell_x, self.grid_width - 1))
        clamped_y: int = max(0, min(cell_y, self.grid_height - 1))

        return clamped_x, clamped_y

    def clear(self) -> None:
        """Clear all cells - call this each frame"""
        self.cells.clear()

    def add_enemy(self, enemy: Enemy) -> None:
        """Add enemy to appropriate cell"""
        cell: tuple[int, int] = self.get_cell_coords(enemy.location)
        if cell not in self.cells:
            self.cells[cell] = []
        self.cells[cell].append(enemy)

    def get_enemies_in_cells(self, cells: Set[tuple[int, int]]) -> List[Enemy]:
        """Get all enemies from a set of cells (tuples for performance)"""
        enemies: List[Enemy] = []
        for cell in cells:
            if cell in self.cells:
                enemies.extend(self.cells[cell])
        return enemies

    def get_cells_around_point(self, location: XYFloat, radius: int = 1) -> Set[tuple[int, int]]:
        """Get cells in a radius around a point - input XYFloat, output tuple set"""
        center_cell: tuple[int, int] = self.get_cell_coords(location)  # Convert XYFloat to tuple
        cells: Set[tuple[int, int]] = set()

        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                cell_x: int = center_cell[0] + dx
                cell_y: int = center_cell[1] + dy
                cell: tuple[int, int] = (cell_x, cell_y)

                if (0 <= cell_x < self.grid_width and
                        0 <= cell_y < self.grid_height):
                    cells.add(cell)

        return cells


class CollisionManager:
    def __init__(self, spatial_grid: SpatialGrid) -> None:
        self.spatial_grid: SpatialGrid = spatial_grid

        # Pre-allocate containers to avoid repeated memory allocation
        self._collision_results: Dict[BaseAmmo, Enemy] = {}
        self._ammo_by_cell: Dict[tuple[int, int], List[BaseAmmo]] = {}
        self._checked_pairs: Set[tuple[BaseAmmo, Enemy]] = set()

    def batch_check_collisions(self, all_ammo: List[BaseAmmo]) -> Dict[BaseAmmo, Enemy]:
        """Optimized batch collision detection - uses tuples internally for speed"""
        # Clear previous results
        self._collision_results.clear()
        self._ammo_by_cell.clear()
        self._checked_pairs.clear()

        # Group ammo by grid cell using tuples for performance
        for ammo in all_ammo:
            # Convert XYFloat location to tuple cell coordinates
            cell: tuple[int, int] = self.spatial_grid.get_cell_coords(ammo.current_location)
            if cell not in self._ammo_by_cell:
                self._ammo_by_cell[cell] = []
            self._ammo_by_cell[cell].append(ammo)

        # Process each cell
        for cell, cell_ammo in self._ammo_by_cell.items():
            # Get all relevant cells (current + adjacent) - all tuples for speed
            relevant_cells: Set[tuple[int, int]] = set()
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    adjacent_x: int = cell[0] + dx
                    adjacent_y: int = cell[1] + dy
                    adjacent_cell: tuple[int, int] = (adjacent_x, adjacent_y)

                    if (0 <= adjacent_x < self.spatial_grid.grid_width and
                            0 <= adjacent_y < self.spatial_grid.grid_height):
                        relevant_cells.add(adjacent_cell)

            # Get enemies from relevant cells
            nearby_enemies: List[Enemy] = self.spatial_grid.get_enemies_in_cells(relevant_cells)

            # Check collisions for ammo in this cell
            self._check_cell_collisions(cell_ammo, nearby_enemies)

        return self._collision_results

    def _check_cell_collisions(self, ammo_list: List[BaseAmmo], enemies: List[Enemy]) -> None:
        """Check collisions between ammo and enemies in a cell"""
        for ammo in ammo_list:
            if ammo in self._collision_results:  # Already hit something
                continue

            ammo_rect: FRect = ammo.get_rect()
            ammo_left: float = ammo_rect.left
            ammo_top: float = ammo_rect.top
            ammo_right: float = ammo_rect.right
            ammo_bottom: float = ammo_rect.bottom
            ammo_bounds: tuple[float, float, float, float] = (ammo_left, ammo_top, ammo_right, ammo_bottom)

            for enemy in enemies:
                # Quick bounds check first
                enemy_rect = enemy.get_rect()
                if (ammo_bounds[2] < enemy_rect.left or  # ammo right < enemy left
                        ammo_bounds[0] > enemy_rect.right or  # ammo left > enemy right
                        ammo_bounds[3] < enemy_rect.top or  # ammo bottom < enemy top
                        ammo_bounds[1] > enemy_rect.bottom):  # ammo top > enemy bottom
                    continue

                # More expensive collision check only if bounds overlap
                if ammo_rect.colliderect(enemy_rect):
                    self._collision_results[ammo] = enemy
                    break  # Each ammo can only hit one enemy


class HighPerformanceCollisionSystem:
    """Main collision system that coordinates everything"""

    def __init__(self, cell_size: int = 64) -> None:
        self.spatial_grid: SpatialGrid = SpatialGrid(cell_size)
        self.collision_manager: CollisionManager = CollisionManager(self.spatial_grid)

        # Statistics for debugging
        self.stats: Dict[str, int] = {
            'enemies_processed': 0,
            'ammo_processed': 0,
            'collisions_found': 0,
            'cells_used': 0
        }

    def update_enemies(self, enemies: List[Enemy]) -> None:
        """Add all enemies to spatial grid"""
        self.spatial_grid.clear()
        for enemy in enemies:
            self.spatial_grid.add_enemy(enemy)

        self.stats['enemies_processed'] = len(enemies)
        self.stats['cells_used'] = len(self.spatial_grid.cells)

    def check_all_collisions(self, all_weapons_ammo: List[BaseAmmo]) -> Dict[BaseAmmo, Enemy]:
        """Check collisions for all projectiles from all weapons"""
        collisions: Dict[BaseAmmo, Enemy] = self.collision_manager.batch_check_collisions(all_weapons_ammo)

        self.stats['ammo_processed'] = len(all_weapons_ammo)
        self.stats['collisions_found'] = len(collisions)

        return collisions

    def get_debug_info(self) -> str:
        """Get performance statistics"""
        enemies_count: int = self.stats['enemies_processed']
        ammo_count: int = self.stats['ammo_processed']
        collisions_count: int = self.stats['collisions_found']
        cells_count: int = self.stats['cells_used']

        return (f"Enemies: {enemies_count}, "
                f"Ammo: {ammo_count}, "
                f"Collisions: {collisions_count}, "
                f"Cells: {cells_count}")


# Integration helper for weapons
class WeaponCollisionHelper:
    """Helper to integrate weapons with the new collision system"""

    def __init__(self) -> None:
        self.collision_system: HighPerformanceCollisionSystem | None = None
        self.all_ammo: List[BaseAmmo] = []  # Collect ammo from all weapons
        self.collision_results: Dict[BaseAmmo, Enemy] = {}

    def set_collision_system(self, collision_system: HighPerformanceCollisionSystem) -> None:
        self.collision_system = collision_system

    def register_ammo(self, weapon_ammo: List[BaseAmmo]) -> None:
        """Register ammo from a weapon for batch processing"""
        self.all_ammo.extend(weapon_ammo)

    def process_all_collisions(self) -> Dict[BaseAmmo, Enemy]:
        """Process all registered ammo at once"""
        if not self.collision_system:
            return {}

        self.collision_results = self.collision_system.check_all_collisions(self.all_ammo)
        return self.collision_results

    def clear_frame(self) -> None:
        """Clear data for next frame"""
        self.all_ammo.clear()
        self.collision_results.clear()

    def did_ammo_hit(self, ammo: BaseAmmo) -> Enemy | None:
        """Check if specific ammo hit an enemy"""
        return self.collision_results.get(ammo, None)