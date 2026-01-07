from django.utils import timezone
from django.http import JsonResponse
from django.urls import resolve
from .models import Exam

class ExamTimingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == 'POST' and self._is_exam_submission(request):
            timing_check = self._check_exam_timing(request)
            if not timing_check['valid']:
                return JsonResponse({
                    'error':timing_check['message'],
                    'status':'forbidden'
                }, status=403)
            
        response = self.get_response(request)
        return response
    
    def _is_exam_submission(self, request):
        try:
            resolved = resolve(request.path)
            exam_views = ['exam_submit','submit_exam','exam_submission']
            return (resolved.url_name in exam_views or
                    ('exam' in request.path.lower() and 'submit' in request.path.lower()))
        except:
            return False
        
    def _check_exam_timing(self, request):
        try:
            exam_id = (request.POST.get('exam_id') or 
                       request.POST.get('exam') or
                       request.POST.get('exam_id'))
            if not exam_id:
                return {'valid':False, 'message':'Exam ID not provided'}
            
            exam = Exam.objects.get(exam_id=exam_id)
            current_time = timezone.now()

            if current_time > exam.end_time:
                return {
                    'valid':False,
                    'message':f'Exam has not yet started yet. It begin at {exam.start_time.strftime("%Y-%m-%d %H:%M")}'
                }
            
            if request.user.is_authenticated:
                from .models import ExamSubmission
                existing_submissions = ExamSubmission.objects.filter(
                    student=request.user.student,
                    exam=exam
                ).exists()

                if existing_submissions:
                    return {
                        'valid':False,
                        'message':'You have already submitted this exam'
                    }
                
            return {'valid':True,'message':'Valid Submission time'}
        except Exam.DoesNotExist:
            return {'valid':False, 'message':'Exam not found'}
        except AttributeError:
            return {'valid':False, 'message':'Student account not found'}
        except Exception as e:
            return {'valid':False, 'message':f'Error checking exam timing: {str(e)}'}