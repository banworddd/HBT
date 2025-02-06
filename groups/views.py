from django.shortcuts import render, redirect, get_object_or_404

from .models import Groups, GroupSubscribers, GroupPosts, GroupPostsEdits, GroupPostsComments, GroupPostReaction, GroupPostsCommentsReactions
from .forms import GroupPostForm, GroupCreationForm, GroupPostCommentForm
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
        form = GroupCreationForm(request.POST, request.FILES)
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

    # Получение поста и информации о группе
    post = get_object_or_404(GroupPosts, slug=post_slug)
    group = post.group
    is_admin = GroupSubscribers.objects.filter(group=group, user=request.user, is_admin=True).exists()
    is_subscriber = GroupSubscribers.objects.filter(group=group, user=request.user).exists()

    # Получение комментариев и реакций
    comments = GroupPostsComments.objects.filter(post=post)
    comments_reactions = {}
    user_comment_reactions = {}

    # Проверка и получение реакций пользователя
    if is_subscriber:
        user_sub = GroupSubscribers.objects.get(group=group, user=request.user)

        for comment in comments:
            reactions = GroupPostsCommentsReactions.objects.filter(comment=comment)
            comments_reactions[comment.id] = {
                'L': reactions.filter(status='L').count(),
                'D': reactions.filter(status='D').count(),
                'H': reactions.filter(status='H').count()
            }
            user_reaction = reactions.filter(react_user=user_sub).first()
            user_comment_reactions[comment.id] = user_reaction.status if user_reaction else None

    # Работа с реакциями к посту
    l_reactions = GroupPostReaction.objects.filter(post=post, status='L').count()
    d_reactions = GroupPostReaction.objects.filter(post=post, status='D').count()
    h_reactions = GroupPostReaction.objects.filter(post=post, status='H').count()
    user_post_reaction = None

    if is_subscriber:
        user_sub = GroupSubscribers.objects.get(group=group, user=request.user)
        post_reaction = GroupPostReaction.objects.filter(post=post, react_user=user_sub).first()
        user_post_reaction = post_reaction.status if post_reaction else None

    # Форма добавления комментариев
    if request.method == 'POST':
        form = GroupPostCommentForm(request.POST)
        if form.is_valid() and is_subscriber:
            comment = form.save(commit=False)
            comment.post = post
            comment.comment_author = GroupSubscribers.objects.get(group=group, user=request.user)
            comment.save()
            return redirect('post', post_slug=post_slug)
    else:
        form = GroupPostCommentForm()

    # Получение истории изменений поста
    post_edits = GroupPostsEdits.objects.filter(post=post)

    # Контекст для шаблона
    context = {
        'post': post,
        'is_admin': is_admin,
        'post_edits': post_edits,
        'is_subscriber': is_subscriber,
        'comments': comments,
        'form': form,
        'l_reactions': l_reactions,
        'd_reactions': d_reactions,
        'h_reactions': h_reactions,
        'user_post_reaction': user_post_reaction,
        'comments_reactions': comments_reactions,
        'user_comment_reactions': user_comment_reactions,
    }

    return render(request, 'groups/post.html', context)

def sendreaction(request, post_slug, reaction):
    redirect_response = check_user_status(request)
    if redirect_response:
        return redirect_response

    post = get_object_or_404(GroupPosts, slug=post_slug)
    user_sub = GroupSubscribers.objects.get(group=post.group, user=request.user)
    reaction_exists = GroupPostReaction.objects.filter(post=post, react_user=user_sub).exists()
    if reaction_exists:
        reaction_exists = GroupPostReaction.objects.get(post=post, react_user=user_sub)
        if reaction_exists.status == reaction:
            reaction_exists.delete()
            return redirect('post',post_slug=post.slug)
        else:
            reaction_exists.delete()
            new_reaction = GroupPostReaction.objects.create(post=post, react_user=user_sub, status=reaction)
            new_reaction.save()
            return redirect('post',post_slug=post.slug)
    else:
        new_reaction = GroupPostReaction.objects.create(post=post, react_user=user_sub, status=reaction)
        new_reaction.save()
        return redirect('post', post_slug=post.slug)

def commentreaction(request, comment_id, reaction):
    redirect_response = check_user_status(request)
    if redirect_response:
        return redirect_response

    is_subscriber = get_object_or_404(GroupSubscribers, user=request.user)
    comment = get_object_or_404(GroupPostsComments, id=comment_id)
    post = GroupPosts.objects.get(id=comment.post_id)
    reaction_exists = GroupPostsCommentsReactions.objects.filter(comment=comment, react_user=is_subscriber).exists()
    if reaction_exists:
        existing_reactions = GroupPostsCommentsReactions.objects.get(comment=comment, react_user=is_subscriber)
        if existing_reactions.status == reaction:
            existing_reactions.delete()
            return redirect('post', post_slug=post.slug)
        else:
            existing_reactions.delete()
            new_reaction = GroupPostsCommentsReactions.objects.create(comment=comment, react_user=is_subscriber, status=reaction)
            new_reaction.save()
            return redirect('post', post_slug=post.slug)
    else:
        new_reaction = GroupPostsCommentsReactions.objects.create(comment=comment, react_user=is_subscriber, status=reaction)
        new_reaction.save()
        return redirect('post', post_slug=post.slug)




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
        form = GroupCreationForm(request.POST, request.FILES, instance=group)
        if form.is_valid():
            group.name = form.cleaned_data['name'].lower()
            group.public_name = form.cleaned_data['public_name']
            group.description = form.cleaned_data['description']
            group.is_active = form.cleaned_data['is_active']
            group.avatar = form.cleaned_data['avatar']
            group.save()
            return redirect('group', group_name= group.name)
    else:
        # Обработка GET-запроса
        form = GroupCreationForm(instance=group)

    return render(request, 'groups/edit_group.html', context={'form': form})
