from model.category import Category


def test_concolic_category_deactivate_flip():
    # seed: active True
    c = Category("C1", "Food", True)
    assert c.active is True

    # mutate: call deactivate -> flips active to False
    c.deactivate()
    assert c.active is False
