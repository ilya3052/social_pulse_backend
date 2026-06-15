from enum import IntEnum

import numpy as np
from icecream import ic

from social_entities.models import PredictiveModels
from social_entities.utils import Platforms
from stats.models import PostMetrics

class PostStatus(IntEnum):
    OVERRATED = 0
    UNDERRATED = 1

def check_post_stats(model: PredictiveModels, stats: PostMetrics):
    y = model.params.get('intercept')
    std = model.residual_std
    predictable_variable = f'{model.predictable_variable}_count'
    predictable_value = getattr(stats, predictable_variable)
    for param in model.params:
        if hasattr(stats, param):
            param_value = model.params.get(param)
            stats_value = getattr(stats, param)
            if isinstance(stats_value, bool):
                stats_value = int(stats_value)
            y += stats_value * param_value

    residual = y - np.log1p(predictable_value)
    z = residual / std

    if z > 1.5:
        return PostStatus.UNDERRATED
    elif z < -1.5:
        return PostStatus.OVERRATED
    return None

def format_post(post, _id, link, platform):
    match platform:
        case Platforms.VK:
            return f'{link}/?w=wall-{_id}_{post[1]}'
        case Platforms.TG:
            return f'{link}/{post[1]}'
        case _:
            return None

def prepare_post_data(data, group):
    return {
        'link': format_post(data, group.external_id, group.link, Platforms(group.platform.alias)),
        'id': data[1]
    }