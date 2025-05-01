import os
import sys
import time
import csv
import json
from random import randint

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) 
if project_root not in sys.path:
    sys.path.append(project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'simplelms.settings')
import django
django.setup()

from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from core.models import Course, CourseMember, CourseContent, Comment

start_time = time.time()

filepath = './csv_data/'

print("Importing Users...")
try:
    with open(os.path.join(filepath, 'user-data.csv'), newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        users_to_create = []
        existing_usernames = set(User.objects.values_list('username', flat=True))
        
        for row in reader:
            username = row.get('username')
            if username and username not in existing_usernames:
                users_to_create.append(User(
                    username=username,
                    password=make_password(row.get('password', 'password')),
                    email=row.get('email', ''),
                    first_name=row.get('firstname', ''),
                    last_name=row.get('lastname', '')
                ))
                existing_usernames.add(username)
            elif not username:
                 print(f"Skipping row due to missing username: {row}")

        if users_to_create:
            User.objects.bulk_create(users_to_create)
            print(f"-> Created {len(users_to_create)} users.")
        else:
             print("-> No new users to create.")

except FileNotFoundError:
    print(f"ERROR: user-data.csv not found in {filepath}")
except Exception as e:
    print(f"ERROR importing users: {e}")


print("\nImporting Courses...")
try:
    valid_teacher_ids = set(User.objects.values_list('id', flat=True))
    
    with open(os.path.join(filepath, 'course-data.csv'), newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        courses_to_create = []
        
        for row in reader:
            teacher_id_str = row.get('teacher')
            teacher_id = None
            if teacher_id_str:
                try:
                    teacher_id = int(teacher_id_str)
                    if teacher_id not in valid_teacher_ids:
                         print(f"Skipping course '{row.get('name')}' due to invalid teacher ID: {teacher_id}")
                         continue 
                except ValueError:
                    print(f"Skipping course '{row.get('name')}' due to non-integer teacher ID: {teacher_id_str}")
                    continue 
            else:
                 print(f"Skipping course '{row.get('name')}' due to missing teacher ID")
                 continue 

            teacher = User.objects.filter(pk=teacher_id).first()
            if not teacher:
                print(f"Skipping course '{row.get('name')}': Teacher with ID {teacher_id} not found (unexpected).")
                continue

            price_str = row.get('price', '0')
            try:
                price = int(price_str)
            except (ValueError, TypeError):
                price = 0 

            courses_to_create.append(Course(
                name=row.get('name', 'Untitled Course'),
                price=price,
                description=row.get('description', ''),
                teacher=teacher
                
            ))

        if courses_to_create:
            Course.objects.bulk_create(courses_to_create)
            print(f"-> Created {len(courses_to_create)} courses.")
        else:
            print("-> No new courses to create.")

except FileNotFoundError:
    print(f"ERROR: course-data.csv not found in {filepath}")
except Exception as e:
    print(f"ERROR importing courses: {e}")


print("\nImporting Course Members...")
try:
    valid_course_ids = set(Course.objects.values_list('id', flat=True))
    valid_user_ids = set(User.objects.values_list('id', flat=True))
    existing_members = set(CourseMember.objects.values_list('course_id', 'user_id'))

    with open(os.path.join(filepath, 'member-data.csv'), newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        members_to_create = []

        for row in reader:
            try:
                course_id = int(row['course_id'])
                user_id = int(row['user_id'])
                role = row.get('roles', 'std')

                if course_id not in valid_course_ids:
                    print(f"Skipping member: Invalid course ID {course_id}")
                    continue
                if user_id not in valid_user_ids:
                    print(f"Skipping member: Invalid user ID {user_id}")
                    continue
                
                if (course_id, user_id) in existing_members:
                    print(f"Skipping member: User {user_id} already member of course {course_id}")
                    continue

                members_to_create.append(CourseMember(
                    course_id=course_id,
                    user_id=user_id,
                    roles=role
                ))
                existing_members.add((course_id, user_id)) 

            except (KeyError, ValueError, TypeError) as e:
                print(f"Skipping member row due to error: {e} in row {row}")
                continue

        if members_to_create:
            CourseMember.objects.bulk_create(members_to_create)
            print(f"-> Created {len(members_to_create)} course members.")
        else:
            print("-> No new course members to create.")

except FileNotFoundError:
    print(f"ERROR: member-data.csv not found in {filepath}")
except Exception as e:
    print(f"ERROR importing course members: {e}")


print("\nImporting Course Contents...")
try:
    valid_course_ids = set(Course.objects.values_list('id', flat=True))

    with open(os.path.join(filepath, 'contents.json'), 'r', encoding='utf-8') as jsonfile:
        contents_data = json.load(jsonfile)
        contents_to_create = []

        for row in contents_data:
            try:
                course_id = int(row['course_id'])
                if course_id not in valid_course_ids:
                     print(f"Skipping content '{row.get('name')}': Invalid course ID {course_id}")
                     continue
                
                contents_to_create.append(CourseContent(
                    course_id=course_id, 
                    video_url=row.get('video_url', ''),
                    name=row.get('name', 'Untitled Content'),
                    description=row.get('description', '')
                ))
            except (KeyError, ValueError, TypeError) as e:
                 print(f"Skipping content row due to error: {e} in row {row}")
                 continue

        if contents_to_create:
            CourseContent.objects.bulk_create(contents_to_create)
            print(f"-> Created {len(contents_to_create)} course contents.")
        else:
            print("-> No new course contents to create.")

except FileNotFoundError:
    print(f"ERROR: contents.json not found in {filepath}")
except json.JSONDecodeError:
    print(f"ERROR: contents.json is not valid JSON.")
except Exception as e:
    print(f"ERROR importing course contents: {e}")


print("\nImporting Comments...")
try:
    # { content_pk: course_pk }
    content_to_course_map = dict(CourseContent.objects.values_list('pk', 'course_id'))
    # { (user_pk, course_pk): member_pk }
    member_lookup = {(m.user_id, m.course_id): m.pk for m in CourseMember.objects.all()}
    valid_content_ids = set(content_to_course_map.keys())
    valid_user_ids = set(User.objects.values_list('id', flat=True))

    with open(os.path.join(filepath, 'comments.json'), 'r', encoding='utf-8') as jsonfile:
        comments_data = json.load(jsonfile)
        comments_to_create = []

        for row in comments_data:
            try:
                content_id = int(row['content_id'])
                user_id_original = int(row['user_id'])
                comment_text = row.get('comment', '')

                user_id = user_id_original
                if user_id > 50:
                    user_id = randint(5, 40) 

                if content_id not in valid_content_ids:
                    print(f"Skipping comment: Invalid content ID {content_id}")
                    continue
                
                if user_id not in valid_user_ids:
                    print(f"Skipping comment: Invalid user ID {user_id} (original: {user_id_original})")
                    continue
                
                course_id = content_to_course_map.get(content_id)
                if course_id is None: 
                     print(f"Skipping comment: Could not find course for content ID {content_id}")
                     continue

                member_id = member_lookup.get((user_id, course_id))

                if member_id:
                    comments_to_create.append(Comment(
                        content_id=content_id, 
                        member_id=member_id,   
                        comment=comment_text
                    ))
                else:
                    print(f"Skipping comment: No CourseMember found for user {user_id} in course {course_id} (content {content_id})")

            except (KeyError, ValueError, TypeError) as e:
                 print(f"Skipping comment row due to error: {e} in row {row}")
                 continue
        
        if comments_to_create:
            Comment.objects.bulk_create(comments_to_create)
            print(f"-> Created {len(comments_to_create)} comments.")
        else:
             print("-> No new comments to create.")

except FileNotFoundError:
    print(f"ERROR: comments.json not found in {filepath}")
except json.JSONDecodeError:
    print(f"ERROR: comments.json is not valid JSON.")
except Exception as e:
    print(f"ERROR importing comments: {e}")


print("\n-------------------------------------")
print("Data import finished.")
print("Total time: %s seconds" % (time.time() - start_time))
print("-------------------------------------")