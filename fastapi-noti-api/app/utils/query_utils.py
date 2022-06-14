from typing import List


def to_dict(model, *args, exclude: List = None):
    """객체를 딕셔너리로 변환한다."""
    q_dict = {}
    for c in model.__table__.columns:
        if not args or c.name in args:
            if not exclude or c.name not in exclude:
                q_dict[c.name] = getattr(model, c.name)

    return q_dict
