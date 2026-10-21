package data.scripts.hullmods;

import com.fs.starfarer.api.combat.BaseHullMod;
import com.fs.starfarer.api.combat.MutableShipStatsAPI;
import com.fs.starfarer.api.combat.ShipAPI;
import com.fs.starfarer.api.combat.ShipAPI.HullSize;

public class DecapodLocomotion extends BaseHullMod {

    public static final float STRAFE_SPEED_BONUS = 35f;
    public static final float STRAFE_ACCEL_PERCENT = 120f;
    public static final float TURN_BONUS_PERCENT = 30f;
    public static final float TURN_ACCEL_PERCENT = 60f;

    @Override
    public void applyEffectsBeforeShipCreation(HullSize hullSize, MutableShipStatsAPI stats, String id) {
        // Base rotational maneuverability
        stats.getMaxTurnRate().modifyPercent(id, TURN_BONUS_PERCENT);
        stats.getTurnAcceleration().modifyPercent(id, TURN_ACCEL_PERCENT);
        stats.getDeceleration().modifyPercent(id, 40f);
    }

    @Override
    public void advanceInCombat(ShipAPI ship, float amount) {
        if (ship == null || !ship.isAlive()) return;

        MutableShipStatsAPI stats = ship.getMutableStats();
        String id = "decapod_locomotion";

        // Check if the ship is executing a lateral strafe command
        boolean strafing = ship.getEngineController().isStrafingLeft() || ship.getEngineController().isStrafingRight();

        if (strafing) {
            stats.getMaxSpeed().modifyFlat(id, STRAFE_SPEED_BONUS);
            stats.getAcceleration().modifyPercent(id, STRAFE_ACCEL_PERCENT);
        } else {
            stats.getMaxSpeed().unmodify(id);
            stats.getAcceleration().unmodify(id);
        }
    }

    @Override
    public String getDescriptionParam(int index, HullSize hullSize) {
        if (index == 0) return "" + (int) STRAFE_SPEED_BONUS;
        if (index == 1) return "" + (int) (45f + STRAFE_SPEED_BONUS);
        if (index == 2) return "" + (int) STRAFE_ACCEL_PERCENT + "%";
        if (index == 3) return "" + (int) TURN_BONUS_PERCENT + "%";
        if (index == 4) return "" + (int) TURN_ACCEL_PERCENT + "%";
        return null;
    }
}
