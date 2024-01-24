import numpy as np



# --------------------------------------------------------------------------
# function factory for distributions
def create_random_generator(params_dict, key):
    params = params_dict.get(key)
    if params is None:
        raise ValueError(f"No parameters found for key: {key}")

    distribution = params[0]
    params = params[1:]

    if distribution == "uniform":
        low, high = params
        return lambda: np.random.uniform(low, high)
    elif distribution == "normal":
        mu, sigma = params
        return lambda: np.random.normal(mu, sigma)
    elif distribution == "poisson":
        lam = params[0]
        return lambda: np.random.poisson(lam)
    elif distribution == "gamma":
        shape, scale = params
        return lambda: np.random.gamma(shape, scale)
    elif distribution == "exponential":
        scale = params[0]
        return lambda: np.random.exponential(scale)
    else:
        raise ValueError(f"Unknown distribution: {distribution}")

