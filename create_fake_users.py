import random
import sys
from faker import Faker
from api import db, User

def create_fake_users(n):
    """Generate fake users."""
    faker = Faker()
    team_members_choices = ['DPO', 'IG Member', 'Work Council', 'Legal Member']
    for i in range(n):
        user = User(name = faker.name(), 
                    age = random.randint(20, 80), 
                    address = faker.address().replace('\n',', '),
                    phone = faker.phone_number(),
                    email = faker.email(),
                    country = faker.country(),
                    date_of_birth = faker.date_time(),
                    team_member = random.choice(team_members_choices)
                    )
        db.session.add(user)
    db.session.commit()
    print(f'Added {n} faker users to the db.')

if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print('Pass the number of users you want to create as an argument.')
        sys.exit(1)
    create_fake_users(int(sys.argv[1]))