// main function now takes the target coordinates and radius as inputs.
// In a real ZKP context:
// - user_lat, user_lon would be PRIVATE inputs.
// - target_lat, target_lon, radius_meters would be PUBLIC inputs.
fn main(
    user_lat: i64,
    user_lon: i64,
    target_lat: pub i64,
    target_lon: pub i64,
    radius_meters: pub i64,
) {
    // Input bounds (micro-degrees for lat/lon; meters for radius)
    assert(user_lat >= -90_000_000 & user_lat <= 90_000_000, "bad user_lat");
    assert(user_lon >= -180_000_000 & user_lon <= 180_000_000, "bad user_lon");
    assert(target_lat >= -90_000_000 & target_lat <= 90_000_000, "bad target_lat");
    assert(target_lon >= -180_000_000 & target_lon <= 180_000_000, "bad target_lon");
    assert(radius_meters > 0 & radius_meters <= 500, "bad radius");

    let delta_lat = user_lat - target_lat;
    let delta_lon = user_lon - target_lon;

    let dy = (delta_lat * 11132) / 100000;
    let dx = (delta_lon * 11132) / 100000;

    let square_distance = dx * dx + dy * dy;
    let radius_squared = radius_meters * radius_meters;

    assert(square_distance < radius_squared, "User is outside the specified radius");
    println("Proof successful: User is within the specified radius.");
}

// The sqrt_approx function is no longer needed!

// --- TESTS ---

#[test]
fn test_eiffel_tower_success() {
    // Public Inputs: Prove you are within 50m of the Eiffel Tower
    let eiffel_tower_lat: i64 = 48_858_370; // 48.858370
    let eiffel_tower_lon: i64 = 2_294_481; // 2.294481
    let radius: i64 = 50;

    // Private Inputs: User is ~25m away from the center
    let user_lat: i64 = 48_858_550;
    let user_lon: i64 = 2_294_650;

    main(
        user_lat,
        user_lon,
        eiffel_tower_lat,
        eiffel_tower_lon,
        radius,
    );
}

#[test(should_fail_with = "User is outside the specified radius")]
fn test_statue_of_liberty_fail() {
    // Public Inputs: Prove you are within 100m of the Statue of Liberty
    let liberty_lat: i64 = 40_689_247; // 40.689247
    let liberty_lon: i64 = -74_044_502; // -74.044502
    let radius: i64 = 100;

    // Private Inputs: User is far away in another part of the city
    let user_lat: i64 = 40_758_000; // Times Square
    let user_lon: i64 = -73_985_500;

    main(user_lat, user_lon, liberty_lat, liberty_lon, radius);
}
