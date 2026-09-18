from flask import Flask, request, render_template
import math
import os

app = Flask(__name__)


# =========================================================
# PRANDTL-MEYER FUNCTIONS
# =========================================================

def prandtl_meyer(M, gamma=1.4):

    return math.degrees(
        math.sqrt((gamma + 1) / (gamma - 1))
        * math.atan(
            math.sqrt(
                ((gamma - 1) / (gamma + 1)) * (M**2 - 1)
            )
        )
        - math.atan(math.sqrt(M**2 - 1))
    )


def max_nu(gamma=1.4):

    return 90 * (
        math.sqrt((gamma + 1) / (gamma - 1)) - 1
    )


def mach_angle(M):

    return math.degrees(
        math.asin(1 / M)
    )


# =========================================================
# ISENTROPIC RELATIONS
# =========================================================

def isentropic_ratios(M, gamma=1.4):

    f = 1 + ((gamma - 1) / 2) * M**2

    T_T0 = 1 / f

    P_P0 = f ** (
        -gamma / (gamma - 1)
    )

    rho_rho0 = f ** (
        -1 / (gamma - 1)
    )

    return T_T0, P_P0, rho_rho0


# =========================================================
# MACH STAR
# =========================================================

def mach_star(M, gamma=1.4):

    return math.sqrt(
        ((gamma + 1) * M**2)
        /
        (2 + (gamma - 1) * M**2)
    )


# =========================================================
# AREA RATIO
# =========================================================

def area_ratio(M, gamma=1.4):

    return (
        (1 / M)
        *
        (
            (2 / (gamma + 1))
            *
            (
                1 + ((gamma - 1) / 2) * M**2
            )
        )
        ** (
            (gamma + 1)
            /
            (2 * (gamma - 1))
        )
    )


# =========================================================
# FIND MACH NUMBER FROM PRANDTL-MEYER ANGLE
# =========================================================

def mach_from_nu(target_nu, gamma=1.4):

    low = 1.0
    high = 4.0

    while prandtl_meyer(high, gamma) < target_nu:
        high *= 1.5

    for _ in range(100):

        mid = (low + high) / 2

        if prandtl_meyer(mid, gamma) < target_nu:
            low = mid
        else:
            high = mid

    return (low + high) / 2


# =========================================================
# CREATE MACH TABLE
# =========================================================

def create_table(gamma, start, end, step):

    # Calculate number of rows
    rows = int(
        round((end - start) / step)
    ) + 1

    # Maximum 2000 rows
    if rows > 2000:

        raise ValueError(
            "Step size results in too many rows "
            "(maximum 2000 rows)."
        )

    data = []

    # Use integer counter to avoid floating-point errors
    for i in range(rows):

        M = start + (i * step)

        # Round Mach number before calculations
        M = round(M, 10)

        # Isentropic ratios
        T, P, R = isentropic_ratios(
            M,
            gamma
        )

        # Prandtl-Meyer and Mach angle
        # are only valid for supersonic flow
        if M >= 1:

            nu = prandtl_meyer(
                M,
                gamma
            )

            mu = mach_angle(M)

        else:

            nu = ""
            mu = ""

        # Store results
        data.append({

            "M": round(M, 3),

            "Mstar": round(
                mach_star(M, gamma),
                4
            ),

            "nu": (
                round(nu, 4)
                if nu != ""
                else ""
            ),

            "mu": (
                round(mu, 4)
                if mu != ""
                else ""
            ),

            "T": round(
                T,
                6
            ),

            "P": round(
                P,
                6
            ),

            "rho": round(
                R,
                6
            ),

            "area": round(
                area_ratio(M, gamma),
                4
            )
        })

    return data


# =========================================================
# MAIN ROUTE
# =========================================================

@app.route(
    "/",
    methods=["GET", "POST"]
)
def home():

    result = None

    table = None

    error = None


    # =====================================================
    # DEFAULT CALCULATOR VALUES
    # =====================================================

    M1 = 2.0

    gamma = 1.4

    theta = 10.0


    # =====================================================
    # DEFAULT TABLE VALUES
    # =====================================================

    tg = 1.4

    start = 0.01

    end = 5.0

    step = 0.01


    active_tab = "calculator"


    # =====================================================
    # POST REQUEST
    # =====================================================

    if request.method == "POST":

        action = request.form.get(
            "action"
        )


        # =================================================
        # PRANDTL-MEYER CALCULATOR
        # =================================================

        if action == "calc":

            active_tab = "calculator"

            try:

                M1 = float(
                    request.form["M1"]
                )

                gamma = float(
                    request.form["gamma"]
                )

                theta = float(
                    request.form["theta"]
                )


                # -----------------------------------------
                # VALIDATION
                # -----------------------------------------

                if M1 <= 1:

                    raise ValueError(
                        "M₁ must be greater than 1 "
                        "for Prandtl-Meyer expansion."
                    )


                if gamma <= 1:

                    raise ValueError(
                        "γ must be greater than 1."
                    )


                if theta <= 0:

                    raise ValueError(
                        "Turning angle must be greater than 0°."
                    )


                # -----------------------------------------
                # PRANDTL-MEYER ANGLES
                # -----------------------------------------

                nu1 = prandtl_meyer(
                    M1,
                    gamma
                )

                nu2 = nu1 + theta


                # -----------------------------------------
                # MAXIMUM PRANDTL-MEYER ANGLE
                # -----------------------------------------

                if nu2 >= max_nu(gamma):

                    raise ValueError(
                        "Turning angle is too large "
                        "for this γ."
                    )


                # -----------------------------------------
                # FIND FINAL MACH NUMBER
                # -----------------------------------------

                M2 = mach_from_nu(
                    nu2,
                    gamma
                )


                # -----------------------------------------
                # MACH ANGLES
                # -----------------------------------------

                mu1 = mach_angle(M1)

                mu2 = mach_angle(M2)


                # -----------------------------------------
                # ISENTROPIC RATIOS - STATE 1
                # -----------------------------------------

                T1, P1, R1 = isentropic_ratios(
                    M1,
                    gamma
                )


                # -----------------------------------------
                # ISENTROPIC RATIOS - STATE 2
                # -----------------------------------------

                T2, P2, R2 = isentropic_ratios(
                    M2,
                    gamma
                )


                # -----------------------------------------
                # FINAL RESULT
                # -----------------------------------------

                result = {

                    "M1": round(
                        M1,
                        4
                    ),

                    "M2": round(
                        M2,
                        4
                    ),

                    "theta": round(
                        theta,
                        3
                    ),

                    "nu1": round(
                        nu1,
                        3
                    ),

                    "nu2": round(
                        nu2,
                        3
                    ),

                    "mu1": round(
                        mu1,
                        3
                    ),

                    "mu2": round(
                        mu2,
                        3
                    ),

                    "T1": round(
                        T1,
                        5
                    ),

                    "T2": round(
                        T2,
                        5
                    ),

                    "P1": round(
                        P1,
                        5
                    ),

                    "P2": round(
                        P2,
                        5
                    ),

                    "R1": round(
                        R1,
                        5
                    ),

                    "R2": round(
                        R2,
                        5
                    ),

                    "T21": round(
                        T2 / T1,
                        5
                    ),

                    "P21": round(
                        P2 / P1,
                        5
                    ),

                    "R21": round(
                        R2 / R1,
                        5
                    )
                }


            except Exception as e:

                error = str(e)


        # =================================================
        # MACH TABLE
        # =================================================

        elif action == "table":

            active_tab = "table"

            try:

                tg = float(
                    request.form["tg"]
                )

                start = float(
                    request.form["start"]
                )

                end = float(
                    request.form["end"]
                )

                step = float(
                    request.form["step"]
                )


                # -----------------------------------------
                # VALIDATION
                # -----------------------------------------

                if tg <= 1:

                    raise ValueError(
                        "γ must be greater than 1."
                    )


                if start <= 0:

                    raise ValueError(
                        "M start must be greater than 0."
                    )


                if end <= start:

                    raise ValueError(
                        "M end must be greater than M start."
                    )


                if step <= 0:

                    raise ValueError(
                        "M step must be greater than 0."
                    )


                # -----------------------------------------
                # CREATE TABLE
                # -----------------------------------------

                table = create_table(
                    tg,
                    start,
                    end,
                    step
                )


            except Exception as e:

                error = str(e)


    # =====================================================
    # SEND DATA TO HTML
    # =====================================================

    return render_template(

        "index.html",

        result=result,

        table=table,

        error=error,

        active_tab=active_tab,


        # Calculator
        M1=M1,

        gamma=gamma,

        theta=theta,


        # Table
        tg=tg,

        start=start,

        end=end,

        step=step
    )


# =========================================================
# RUN FLASK SERVER
# =========================================================

if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            5000
        )
    )

    app.run(

        host="0.0.0.0",

        port=port
    )
