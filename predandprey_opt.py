import optuna

from predandprey import Simulation


def run_simulation(params):
    sim = Simulation(params)
    ticks = 0
    while sim.has_both_species():
        sim.tick()
        ticks += 1
        if ticks > 1000:
            break
    return ticks


def objective(trial):
    params = {
        "sheep_max_hunger": trial.suggest_int("sheep_max_hunger", 30, 50),
        "wolf_max_hunger": trial.suggest_int("wolf_max_hunger", 30, 40),
        "sheep_reproduction_rate": trial.suggest_float("sheep_reproduction_rate", 0.01, 0.1),
        "wolf_reproduction_rate": trial.suggest_float("wolf_reproduction_rate", 0.01, 0.05),
        "grass_growth_rate": trial.suggest_float("grass_growth_rate", 0.01, 0.05),
    }

    time_alive = run_simulation(params)
    return time_alive


if __name__ == "__main__":
    study = optuna.create_study(direction="maximize")
    study.optimize(objective, n_trials=200)

    print("Best parameters:", study.best_params)
    print("Best score:", study.best_value)
