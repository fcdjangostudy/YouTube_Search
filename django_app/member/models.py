from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    '''
    동작
        follow : 내가 다른 사람을 follow함
        unfollow : 낵 다른사람에게 한 follow를 취소함

    속성
        follow : 내가 다른사람을 follow함
        followers : 나를 follow하고 있는 사람들
        follower : 나를 follow하고 있는 사람
        friend : 서로 follow하고 있는 관계
        friends : 나와 서로 follow하고 있는 모든 관계
        없음 : 내가 follow하고 있는 사람 1명

    following : 내가 follow하고 있는 사람들
    '''
    # 이 User모델을 AUTH_USER_MODEL로 사용하도록 settings.py에 설정
    nickname = models.CharField(max_length=24, null=True, unique=True)

    relations = models.ManyToManyField(
        'self',
        through='Relation',
        symmetrical=False,
    )

    def __str__(self):
        return self.nickname or self.username
        # return self.nickname if self.nickname else self.username

    # def follow(self, user):
    #     if not isinstance(user, User):
    #         raise ValueError("user는 User형 클래스가 아닙니다.")
    #
    #     created_relation, is_exist = self.follow_relations.get_or_create(to_user=user)
    #     if is_exist:
    #         return created_relation
    #     return '이미 팔로우 하셨습니다.'
    #
    # def unfollow(self, user):
    #     Relation.objects.filter(
    #         from_user=self,
    #         to_user=user,
    #     ).delete()

    def is_follow(self, user):
        return self.follow_relations.filter(to_user=user).exists()

    def is_follower(self, user):
        return self.follower_relations.filter(from_user=user).exists()

    def follow_toggle(self, user):
        created_relation, is_exist = self.follow_relations.get_or_create(to_user=user)
        if is_exist:
            return created_relation
        else:
            created_relation.delete()
            return '언팔로우 했습니다.'

    @property
    def following(self):
        relations = self.follow_relations.all()
        return User.objects.filter(pk__in=relations.values('to_user_id'))
        # return [i.to_user for i in self.follow_relations.all()]


    @property
    def follower(self):
        relations = self.follower_relations.all()
        return User.objects.filter(pk__in=relations.values('from_user_id'))


class Relation(models.Model):
    from_user = models.ForeignKey(User, related_name='follow_relations')
    to_user = models.ForeignKey(User, related_name='follower_relations')
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return 'Relations form {} to {}'.format(
            self.from_user,
            self.to_user,
        )

    class Meta:
        unique_together = (
            ('from_user', 'to_user'),
        )


