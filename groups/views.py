from django.shortcuts import render, redirect, get_object_or_404

from .models import Groups, GroupSubscribers, GroupPosts, GroupPostsEdits
from .forms import GroupPostForm, GroupCreationForm
from common.utils import check_user_status

def groups(request):
    redirect_response = check_user_status(request)
    if redirect_response:
        return redirect_response
    groups = Groups.active_groups.all()
    group_info = {}
    for group in groups:
        group_info[group.name] = GroupSubscribers.objects.filter(group=group).count()
    return render (request, 'groups/groups.html', context={'group_info':group_info})

def user_subcriptions(request):
    redirect_response = check_user_status(request)
    if redirect_response:
        return redirect_response
    user_groups = GroupSubscribers.objects.filter(user=request.user)

    return render(request, 'groups/user_subcriptions.html', context={'user_groups':user_groups})

def group(request, group_name):
    redirect_response = check_user_status(request)
    if redirect_response:
        return redirect_response

    form = GroupPostForm()
    group = get_object_or_404(Groups, name=group_name)
    group_admins = GroupSubscribers.objects.filter(group=group, is_admin=True)
    group_posts = GroupPosts.objects.filter(group=group)
    subscribers = GroupSubscribers.objects.filter(group=group).count()
    is_admin = group_admins.filter(user=request.user).exists()
    is_subscriber = GroupSubscribers.objects.filter(group=group, user=request.user).exists()
    if request.method == 'POST':
        form = GroupPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.group = group
            post.author = GroupSubscribers.objects.get(group = group, user=request.user)
            post.author_name = request.user.username
            post.author = GroupSubscribers.objects.get(user=request.user, is_admin=True, group=group)
            post.save()
            return redirect('group', group_name)

    return render(request, 'groups/group.html', context={
        'group': group,
        'group_posts': group_posts,
        'subscribers': subscribers,
        'group_admins': group_admins,
        'form': form,
        'is_admin' : is_admin,
        'is_subscriber' : is_subscriber
    })

def subscribe(request, group_name):
    redirect_response = check_user_status(request)
    if redirect_response:
        return redirect_response

    group = Groups.objects.get(name=group_name)
    if not GroupSubscribers.objects.filter(group=group, user = request.user).exists():
        if group.creator == request.user:
            GroupSubscribers.objects.create(group=group, user=request.user, is_admin=True)
        else:
            GroupSubscribers.objects.create(group=group, user=request.user, is_admin=False)
    return redirect('group', group_name)

def unsubscribe(request, group_name):
    redirect_response = check_user_status(request)
    if redirect_response:
        return redirect_response

    group = Groups.objects.get(name=group_name)
    if GroupSubscribers.objects.filter(group=group, user=request.user).exists():
        GroupSubscribers.objects.filter(group=group, user=request.user).delete()
    return redirect('group', group_name)

def creategroup(request):
    redirect_response = check_user_status(request)
    if redirect_response:
        return redirect_response

    if request.method == 'POST':
        form = GroupCreationForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.creator = request.user
            group.save()
            return redirect('group', group_name=group.name)
    else:
        form = GroupCreationForm()
    return render(request, 'groups/create_group.html', context={'form': form})

def postview(request, post_slug):
    redirect_response = check_user_status(request)
    if redirect_response:
        return redirect_response

    post = GroupPosts.objects.get(slug=post_slug)
    post_edits = GroupPostsEdits.objects.filter(post = post)
    group = post.group
    print(f'1{post.picture1}, 2{post.picture2}, 3{post.picture3}')
    is_admin = GroupSubscribers.objects.filter(group=group, user=request.user, is_admin=True).exists()
    return render(request, 'groups/post.html', context={'post':post, 'is_admin':is_admin, 'post_edits':post_edits})

def deletepost(request, post_slug):
    redirect_response = check_user_status(request)
    if redirect_response:
        return redirect_response

    post = GroupPosts.objects.get(slug=post_slug)
    group = Groups.objects.get(name=post.group.name)
    post.delete()
    return redirect('group', group_name=group.name)

def editpost(request, post_slug):
    redirect_response = check_user_status(request)
    if redirect_response:
        return redirect_response

    post = get_object_or_404(GroupPosts, slug=post_slug)
    group = post.group
    redactor = GroupSubscribers.objects.get(group=group, user=request.user, is_admin=True)
    if not GroupSubscribers.objects.filter(group=group, user=request.user, is_admin=True).exists():
        return redirect('startpage')

    if request.method == 'POST':
        post_previous = post.post
        form = GroupPostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.is_edit = True
            post_edit = GroupPostsEdits.objects.create(post=post, edit_author=redactor, edit_author_name=redactor.user.username, post_previous=post_previous, post_next=post.post )
            post_edit.save()
            post.save()
            return redirect('post', post_slug = post_slug)
    else:
        form = GroupPostForm(instance=post)

    return render(request, 'groups/editpost.html', context={'post':post, 'form':form})

def editgroup(request, group_name):
    redirect_response = check_user_status(request)
    if redirect_response:
        return redirect_response

    # Получение группы
    group = get_object_or_404(Groups, name=group_name)

    # Проверка прав доступа
    if not GroupSubscribers.objects.filter(group=group, user=request.user, is_admin=True).exists():
        return redirect('startpage')

    if request.method == 'POST':
        # Обработка POST-запроса
        form = GroupCreationForm(request.POST, instance=group)
        if form.is_valid():
            name = '@'+form.cleaned_data['name'].lower()
            form.save()
            return redirect('group', group_name=name)
    else:
        # Обработка GET-запроса
        form = GroupCreationForm(instance=group)

    return render(request, 'groups/edit_group.html', context={'form': form})
