import functools
import scipy
import numpy as np


def compute_bertrand_prices(df, params, quad_draws, quad_weights):
    """Computes Bertrand-Nash prices for all products in all markets.

    Args:
        df (pandas.DataFrame): DataFrame of simulated data for products containing
            observable and unobservable product characteristics, prices, costs, and
            marginal costs.
        params (dict): Model parameters.
        quad_draws (np.ndarray): 1d array of shape (n_quad_points,)
            containing the Hermite quadrature points.
        quad_weights (np.ndarray): 1d array of shape (n_quad_points,)
            containing the associated Hermite quadrature weights.

    Returns:
        numpy.ndarray: 1d array of shape (num_markets * num_products,) containing the
        Bertrand-Nash prices for all products in all markets.
    """
    num_markets = len(df.index.get_level_values("market").unique())
    num_products = len(df.index.get_level_values("product").unique())

    # Create partial function that fixed all arguments except price.
    get_prices = functools.partial(
        supply_foc,
        params=params,
        x_0=df["obs_char_0"].to_numpy(),
        x_1=df["obs_char_1"].to_numpy(),
        xi=df["xi"].to_numpy(),
        marginal_costs=df["marginal_costs"].to_numpy(),
        num_markets=num_markets,
        num_products=num_products,
        quad_draws=quad_draws,
        quad_weights=quad_weights,
    )
    # Find prices using fixed point algorithm from scipy library.
    start_prices = df["marginal_costs"].to_numpy()
    price_bertrand = scipy.optimize.fsolve(func=get_prices, x0=start_prices)
    return price_bertrand


def supply_foc(
    price,
    params,
    x_0,
    x_1,
    xi,
    marginal_costs,
    num_markets,
    num_products,
    quad_draws,
    quad_weights,
):
    """First order condition for the Bertrand-Nash prices.

    Args:
        price (numpy.ndarray): 1d array of shape (num_markets * num_products,) containing
            the prices for all products in all markets.
        params (dict): Model parameters.
        x_0 (numpy.ndarray): 1d array of shape (num_markets * num_products,) containing
            the first observable characteristic (constant) for all products in all
            markets.
        x_1 (numpy.ndarray): 1d array of shape (num_markets * num_products,) containing
            the second observable characteristic for all products in all markets.
        xi (numpy.ndarray): 1d array of shape (num_markets * num_products,) containing
            the unobservable product characteristics for all products in all markets.
        marginal_costs (numpy.ndarray): 1d array of shape (num_markets * num_products,)
            containing the marginal costs for all products in all markets.
        num_markets (int): Number of markets.
        num_products (int): Number of products.
        quad_draws (np.ndarray): 1d array of shape (n_quad_points,)
            containing the Hermite quadrature points.
        quad_weights (np.ndarray): 1d array of shape (n_quad_points,)
            containing the associated Hermite quadrature weights.
    Returns:
        numpy.ndarray: 1d array of shape (num_markets * num_products,) containing the
            first order conditions for the Bertrand-Nash prices for all products in all
            markets. This is zero if prices are Bertrand-Nash prices.
    """

    # Convert inputs to numpy arrays to speed up the following steps.
    delta = compute_mean_utility(params, x_0, x_1, price, xi)
    shares, shares_individual = compute_shares(
        params=params,
        x_0=x_0,
        x_1=x_1,
        delta=delta,
        num_markets=num_markets,
        num_products=num_products,
        quad_draws=quad_draws,
        quad_weights=quad_weights,
        return_individual=True,
    )
    # Single-product firms: the ownership matrix is the identity.
    ownership = np.eye(num_products)

    # Solve the pricing FOC market by market (cross-price effects are within-market).
    markup = np.empty(num_markets * num_products)
    for t in range(num_markets):
        sl = slice(t * num_products, (t + 1) * num_products)
        share_deriv_inv = _compute_share_derivatives_inv(
            shares_ind=shares_individual[t],
            quad_weights=quad_weights,
            params=params,
            ownership=ownership,
        )
        markup[sl] = share_deriv_inv @ shares[t]

    out = price + markup - marginal_costs
    return out


def compute_mean_utility(params, x_0, x_1, price, xi):
    """Compute the mean utility across consumers for all products in all markets.

    Args:
        params (dict): Model parameters.
        x_0 (numpy.ndarray): 1d array of shape (num_markets * num_products,) containing
            the first observable characteristic (constant) for all products in all
            markets.
        x_1 (numpy.ndarray): 1d array of shape (num_markets * num_products,) containing
            the second observable characteristic for all products in all markets.
        price (numpy.ndarray): 1d array of shape (num_markets * num_products,) containing
            the prices for all products in all markets.
        xi (numpy.ndarray): 1d array of shape (num_markets * num_products,) containing
            the unobservable product characteristics for all products in all markets.

    Returns:
        numpy.ndarray: 1d array of shape (num_markets * num_products,) containing
            the mean utility across consumers for all products in all markets.
    """

    delta = (
        params["beta"][0] * x_0 + params["beta"][1] * x_1 + params["alpha"] * price + xi
    )
    return delta


def compute_shares(
    params, x_0, x_1, delta, num_markets, num_products, quad_draws, quad_weights,
    return_individual=False,
):
    """Compute shares by integrating over utilities.

    Args:
        params (dict): Model parameters.
        x_0 (numpy.ndarray): 1d array of shape (num_markets * num_products,) containing
            the first observable characteristic (constant) for all products in all
            markets.
        x_1 (numpy.ndarray): 1d array of shape (num_markets * num_products,) containing
            the second observable characteristic for all products in all markets.
        delta (numpy.ndarray): 1d array of shape (num_markets * num_products,) containing
            the mean utility across consumers for all products in all markets.
        num_markets (int): Number of markets.
        num_products (int): Number of products.
        quad_draws (np.ndarray): 1d array of shape (n_quad_points,)
            containing the Hermite quadrature points.
        quad_weights (np.ndarray): 1d array of shape (n_quad_points,)
            containing the associated Hermite quadrature weights.

    Returns:
        numpy.ndarray: 2d array of shape (num_markets, num_products) containing the
            market shares for all products in all markets.
    """

    # Calculate the shock values to be integrated for each quadrature point and product.
    # Shape is then (num_products * num_markets, num_quad_points).
    mu = np.outer(x_0 * params["sigma"][0] + x_1 * params["sigma"][1], quad_draws)
    # Calculate the exponential of the utility and reshape
    exp_util = np.exp(mu + delta[:, np.newaxis]).reshape(
        num_markets, num_products, quad_draws.shape[0]
    )
    # Calculate shares
    shares = exp_util / (1 + exp_util.sum(axis=1)[:, np.newaxis, :])
    # Weight the shares with the integration weights
    shares_weighted = shares @ quad_weights
    if return_individual:
        # Also return the individual (per quadrature node) choice probabilities,
        # of shape (num_markets, num_products, n_quad_points).
        return shares_weighted, shares
    return shares_weighted


def _compute_share_derivatives_inv(shares_ind, quad_weights, params, ownership):
    """Invert the ownership-weighted share-derivative matrix for one market.

    Builds the full random-coefficient Jacobian of market shares with respect to
    prices,
        d s_j / d p_k = alpha * sum_i w_i s_ij (1{j=k} - s_ik),
    takes its element-wise product with the ownership matrix, and returns the inverse,
    as used in the multiproduct Bertrand-Nash pricing FOC.

    Args:
        shares_ind (np.ndarray): 2d array of shape (num_products, n_quad_points)
            containing the individual (per quadrature node) choice probabilities
            for one particular market.
        quad_weights (np.ndarray): 1d array of shape (n_quad_points,) containing
            the associated quadrature weights.
        params (dict): Model parameters.
        ownership (np.ndarray): 2d array of shape (num_products, num_products);
            element (j, k) is 1 if products j and k are produced by the same firm
            and 0 otherwise.

    Returns:
        np.ndarray: 2d array of shape (num_products, num_products), the inverse of
            the ownership-weighted matrix of share derivatives.
    """
    alpha = params["alpha"]
    # Aggregate shares s_j = sum_i w_i s_ij.
    agg = shares_ind @ quad_weights
    # Cross term sum_i w_i s_ij s_ik.
    cross = (shares_ind * quad_weights) @ shares_ind.T
    # Matrix of share derivatives d s_j / d p_k.
    share_deriv = alpha * (np.diag(agg) - cross)
    return np.linalg.inv(ownership * share_deriv)
