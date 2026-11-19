"""Hardware checks for Raspberry Pi boards this scoreboard has to treat differently."""

from pathlib import Path

# Stock rpi-rgb-led-matrix defaults used on Pi 3 / 4 / Zero 2 W.
DEFAULT_PWM_BITS = 11
DEFAULT_PWM_LSB_NS = 130

# A Pi Zero W (BCM2835, one core, 512MB) cannot refresh a panel at 11-bit PWM
# and still leave time for Python and the SDIO Wi-Fi chip. These values match
# the rpi-rgb-led-matrix guidance for Pi 1 / Zero: slowdown 0, fewer PWM bits,
# and a refresh cap so the realtime thread does not sit at 100% CPU.
PI_ZERO_PWM_BITS = 7
PI_ZERO_PWM_LSB_NS = 300
PI_ZERO_GPIO_SLOWDOWN = 0
PI_ZERO_LIMIT_REFRESH_HZ = 100
PI_ZERO_MAX_PIXELS = 64 * 32


def device_model():
    """Return the device-tree model string, or '' when this is not a Pi."""
    for path in ("/proc/device-tree/model", "/sys/firmware/devicetree/base/model"):
        try:
            text = Path(path).read_bytes().replace(b"\x00", b"").decode().strip()
        except OSError:
            continue
        if text:
            return text
    return ""


def is_pi_zero_v1(model=None):
    """True for the original Pi Zero, Zero W, Zero WH, and Pi 1.

    Those boards are a single-core ARMv6. The Pi Zero 2 W is a quad-core
    Cortex-A53 (same family as the Pi 3) and is not included.
    """
    if model is None:
        model = device_model()
    lowered = (model or "").lower()
    if not lowered.startswith("raspberry pi"):
        return False
    if "zero 2" in lowered:
        return False
    if "zero" in lowered:
        return True
    # "Raspberry Pi Model B" / "Model A Plus". Later boards are "Raspberry Pi 3 Model B".
    if lowered.startswith("raspberry pi model "):
        return True
    if "compute module" in lowered and not any(
        token in lowered for token in ("compute module 3", "compute module 4", "compute module 5")
    ):
        return True
    return False


def resolve_matrix_timing(args, model=None):
    """Fill in matrix timing, including lighter defaults on a Pi Zero / Pi 1.

    ``gpio_slowdown`` is None when the library default should be left alone.
    ``note`` is a startup message when the Pi Zero defaults were applied.
    """
    pwm_bits = args.led_pwm_bits
    lsb_ns = args.led_pwm_lsb_nanoseconds
    slowdown = args.led_slowdown_gpio
    limit_hz = args.led_limit_refresh
    note = None

    if is_pi_zero_v1(model) and not getattr(args, "led_no_pi_tune", False):
        if pwm_bits is None:
            pwm_bits = PI_ZERO_PWM_BITS
        if lsb_ns is None:
            lsb_ns = PI_ZERO_PWM_LSB_NS
        if slowdown is None:
            slowdown = PI_ZERO_GPIO_SLOWDOWN
        if limit_hz == 0:
            limit_hz = PI_ZERO_LIMIT_REFRESH_HZ

        model_name = model if model is not None else device_model()
        pixels = args.led_rows * args.led_cols * max(1, args.led_chain)
        note = (
            f"{model_name or 'Raspberry Pi Zero'} detected. "
            f"Using low-CPU matrix timing (pwm_bits={pwm_bits}, gpio_slowdown={slowdown}, "
            f"pwm_lsb_nanoseconds={lsb_ns}, refresh cap {limit_hz} Hz) so the panel and Wi-Fi "
            "can share one core. Pass the matching --led-* flag to override a value, or "
            "--led-no-pi-tune to keep stock timing."
        )
        if pixels > PI_ZERO_MAX_PIXELS:
            note += (
                f" This panel is {args.led_cols}x{args.led_rows}"
                f" with chain {args.led_chain} ({pixels} pixels). "
                "64x32 is the size this board can refresh reliably."
            )
    else:
        if pwm_bits is None:
            pwm_bits = DEFAULT_PWM_BITS
        if lsb_ns is None:
            lsb_ns = DEFAULT_PWM_LSB_NS

    return {
        "pwm_bits": pwm_bits,
        "pwm_lsb_nanoseconds": lsb_ns,
        "gpio_slowdown": slowdown,
        "limit_refresh_hz": limit_hz,
        "note": note,
    }
