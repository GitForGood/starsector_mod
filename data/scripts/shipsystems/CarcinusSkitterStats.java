package data.scripts.shipsystems;

import com.fs.starfarer.api.combat.MutableShipStatsAPI;
import com.fs.starfarer.api.impl.combat.BaseShipSystemScript;
import com.fs.starfarer.api.plugins.ShipSystemStatsScript;

public class CarcinusSkitterStats extends BaseShipSystemScript {

    public static final float SPEED_BONUS = 75f;
    public static final float ACCEL_BONUS = 300f;
    public static final float TURN_SPEED_BONUS = 25f;

    @Override
    public void apply(MutableShipStatsAPI stats, String id, State state, float effectLevel) {
        if (state == ShipSystemStatsScript.State.OUT) {
            stats.getMaxSpeed().unmodify(id);
            stats.getMaxTurnRate().unmodify(id);
        } else {
            stats.getMaxSpeed().modifyFlat(id, SPEED_BONUS * effectLevel);
            stats.getAcceleration().modifyPercent(id, ACCEL_BONUS * effectLevel);
            stats.getDeceleration().modifyPercent(id, ACCEL_BONUS * effectLevel);
            stats.getTurnAcceleration().modifyFlat(id, 40f * effectLevel);
            stats.getTurnAcceleration().modifyPercent(id, 200f * effectLevel);
            stats.getMaxTurnRate().modifyFlat(id, TURN_SPEED_BONUS * effectLevel);
            stats.getMaxTurnRate().modifyPercent(id, 100f * effectLevel);
        }
    }

    @Override
    public void unapply(MutableShipStatsAPI stats, String id) {
        stats.getMaxSpeed().unmodify(id);
        stats.getMaxTurnRate().unmodify(id);
        stats.getTurnAcceleration().unmodify(id);
        stats.getAcceleration().unmodify(id);
        stats.getDeceleration().unmodify(id);
    }

    @Override
    public StatusData getStatusData(int index, State state, float effectLevel) {
        if (index == 0) {
            return new StatusData("skitter drive active: +" + (int) SPEED_BONUS + " top speed", false);
        } else if (index == 1) {
            return new StatusData("lateral surge: +" + (int) ACCEL_BONUS + "% acceleration", false);
        }
        return null;
    }
}
