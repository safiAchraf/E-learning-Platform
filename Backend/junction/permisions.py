def IsLearner(user):
    return user.groups.filter(name='learner').exists()
def IsParent(user):
    return user.groups.filter(name='parent').exists()
def IsInstructor(user):
    return user.groups.filter(name='instructor').exists()
